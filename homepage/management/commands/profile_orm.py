from datetime import date

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.test.utils import CaptureQueriesContext

from events.models import Event
from organizations.models import Organization
from participants.models import Participant
from registrations.models import Registration


class Command(BaseCommand):
    help = "Измерить N+1 на трёх временных регистрациях; все созданные записи откатываются."

    def handle(self, *args, **options):
        with transaction.atomic():
            organization = Organization.objects.create(name="Учебная организация", city="Москва", address="Адрес", phone="123")
            event = Event.objects.create(organization=organization, title="Учебная акция", event_date=date(2026, 11, 18), city="Москва", address="Адрес", max_participants=100)
            ids = []
            for number in range(3):
                person = Participant.objects.create(full_name=f"Учебный донор {number}", birth_date=date(1990, 1, 1), phone="123", blood_type="O+")
                ids.append(Registration.objects.create(event=event, participant=person, registration_date=date(2026, 11, 18)).pk)
            with CaptureQueriesContext(connection) as naive:
                for item in Registration.objects.filter(pk__in=ids):
                    assert item.participant.full_name and item.event.organization.name
            with CaptureQueriesContext(connection) as optimized:
                for item in Registration.objects.filter(pk__in=ids).select_related("participant", "event__organization"):
                    assert item.participant.full_name and item.event.organization.name
            with CaptureQueriesContext(connection) as projected:
                assert len(list(Registration.objects.filter(pk__in=ids).for_listing())) == 3
            with CaptureQueriesContext(connection) as detail_naive:
                item = Registration.objects.get(pk=ids[0])
                assert item.participant.full_name and item.event.title
            with CaptureQueriesContext(connection) as detail_optimized:
                item = Registration.objects.select_related("participant", "event").get(pk=ids[0])
                assert item.participant.full_name and item.event.title
            self.stdout.write(f"Список 3 регистраций: без оптимизации {len(naive)}, select_related {len(optimized)}, annotate/values {len(projected)}")
            self.stdout.write(f"Карточка регистрации: без оптимизации {len(detail_naive)}, select_related {len(detail_optimized)}")
            transaction.set_rollback(True)
        self.stdout.write("Рабочие данные не изменены.")
