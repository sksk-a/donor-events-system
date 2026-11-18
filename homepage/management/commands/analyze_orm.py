from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext

from registrations.models import Registration


class Command(BaseCommand):
    help = "Анализ реальных ORM-запросов без изменения данных; --toolbar проверяет SQL-панель DDT."

    def add_arguments(self, parser):
        parser.add_argument("--toolbar", action="store_true", help="Требует DJANGO_DEBUG_TOOLBAR=1 и DEBUG=True")

    def handle(self, *args, **options):
        ids = list(Registration.objects.order_by("pk").values_list("pk", flat=True)[:5])
        if ids:
            with CaptureQueriesContext(connection) as naive:
                for item in Registration.objects.filter(pk__in=ids):
                    assert item.participant.full_name and item.event.organization.name
            with CaptureQueriesContext(connection) as optimized:
                for item in Registration.objects.filter(pk__in=ids).select_related("participant", "event__organization"):
                    assert item.participant.full_name and item.event.organization.name
            with CaptureQueriesContext(connection) as projected:
                list(Registration.objects.filter(pk__in=ids).for_listing())
            with CaptureQueriesContext(connection) as detail_naive:
                item = Registration.objects.get(pk=ids[0])
                assert item.participant.full_name and item.event.title
            with CaptureQueriesContext(connection) as detail_optimized:
                item = Registration.objects.select_related("participant", "event").get(pk=ids[0])
                assert item.participant.full_name and item.event.title
            self.stdout.write(f"Список {len(ids)}: без оптимизации {len(naive)}, select_related {len(optimized)}, annotate/values {len(projected)}")
            self.stdout.write(f"Карточка: без оптимизации {len(detail_naive)}, select_related {len(detail_optimized)}")
            self.stdout.write("SQL списка: " + projected[0]["sql"])
            self.stdout.write("SQL карточки: " + detail_optimized[0]["sql"])
        else:
            self.stdout.write("Регистраций пока нет. Для воспроизводимого замера на 3 временных записях: manage.py profile_orm.")
        if options["toolbar"]:
            self.check_toolbar()

    def check_toolbar(self):
        if not settings.DEBUG_TOOLBAR_ENABLED:
            raise CommandError("Включите DJANGO_DEBUG_TOOLBAR=1 при DEBUG=True.")
        from debug_toolbar.toolbar import DebugToolbar

        toolbars = []

        def collect(sender, toolbar, **kwargs):
            toolbars.append(toolbar)

        DebugToolbar._created.connect(collect, weak=False)
        try:
            response = Client(HTTP_HOST="127.0.0.1", REMOTE_ADDR="127.0.0.1").get("/registrations/")
            if response.status_code != 200 or not toolbars or b'djDebug' not in response.content:
                raise CommandError("Toolbar не появился в локальном HTML-ответе.")
            stats = toolbars[-1].get_panel_by_id("SQLPanel").get_stats()
            self.stdout.write(f"DDT: HTTP {response.status_code}; SQL-панель записала {len(stats.get('queries', []))} запросов.")
        finally:
            DebugToolbar._created.disconnect(collect)
