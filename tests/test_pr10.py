"""ПР10: QuerySet, вычисляемое поле, slug и общие данные шаблонов."""
from datetime import date
from io import StringIO
import os
from pathlib import Path
import subprocess
import sys

from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext

from events.models import Event
from events.querysets import with_free_places
from registrations.models import Registration


def test_generated_field_recalculates_in_database(orm_database):
    item = Event.objects.get(pk=1)
    assert item.is_large is False
    item.max_participants = 100
    item.save(update_fields=["max_participants"])
    item.refresh_from_db()
    assert item.is_large is True
    Event.objects.filter(pk=1).update(max_participants=99)
    item.refresh_from_db()
    assert item.is_large is False


def test_slug_route_and_stable_absolute_url(client, orm_database):
    item = Event.objects.get(pk=1)
    assert item.slug and item.slug.isascii()
    url = item.get_absolute_url()
    assert client.get(url).status_code == 200
    assert client.get("/events/1/").status_code == 200
    assert client.get("/events/by-slug/missing/").status_code == 404
    item.title = "Другое название"
    item.save()
    assert item.get_absolute_url() == url
    assert "Другое название" in client.get(url).content.decode()


def test_new_events_get_distinct_transliterated_slugs(orm_database):
    fields = dict(organization_id=1, title="День донора", event_date=date(2026, 11, 18), city="Москва", address="Адрес", max_participants=10)
    one = Event.objects.create(**fields)
    two = Event.objects.create(**fields)
    assert one.slug.startswith("den-donora") and one.slug != two.slug
    assert one.slug.isascii() and two.slug.isascii()


def test_context_processor_on_multiple_pages(client, orm_database):
    for url in ["/", "/events/", "/registrations/"]:
        response = client.get(url)
        assert response.context["site_name"] == "Донорские мероприятия"
        assert response.context["events_count"] == Event.objects.count()
        assert "Мероприятия (1)" in response.content.decode()


def test_queryset_statuses_date_and_occupied_places(orm_database):
    item = Registration.objects.create(event_id=1, participant_id=1, registration_date=date(2026, 11, 18))
    assert Registration.objects.active().get().pk == item.pk
    assert Registration.objects.for_date(date(2026, 11, 18)).count() == 1
    assert Registration.objects.for_date(date(2026, 11, 19)).count() == 0
    assert with_free_places().get(pk=1).free_places == 49
    item.cancel()
    assert Registration.objects.active().count() == 0
    assert Registration.objects.cancelled().get().pk == item.pk
    assert Registration.objects.occupied().count() == 0
    assert with_free_places().get(pk=1).free_places == 50
    item.status = Registration.Status.ATTENDED
    item.save()
    assert Registration.objects.completed().get().pk == item.pk
    assert Registration.objects.active().count() == 0


def test_values_listing_is_one_join_query(orm_database):
    Registration.objects.create(event_id=1, participant_id=1, registration_date=date(2026, 11, 18))
    with CaptureQueriesContext(connection) as queries:
        rows = list(Registration.objects.for_listing())
        assert rows[0]["participant_name"] == "Иванов Иван Иванович"
        assert rows[0]["organization_name"] == "Красный Крест"
    assert len(queries) == 1


def test_statistics_status_counts(client, orm_database):
    one = Registration.objects.create(event_id=1, participant_id=1, registration_date=date(2026, 11, 18))
    Registration.objects.create(event_id=1, participant_id=2, registration_date=date(2026, 11, 18), status=Registration.Status.ATTENDED)
    totals = client.get("/registrations/statistics/").context["registration_totals"]
    assert (totals["total"], totals["active"], totals["cancelled"], totals["completed"]) == (2, 1, 0, 1)
    one.cancel()
    totals = client.get("/registrations/statistics/").context["registration_totals"]
    assert (totals["active"], totals["cancelled"], totals["completed"]) == (0, 1, 1)


def test_query_profile_keeps_working_data(orm_database):
    before = (Event.objects.count(), Registration.objects.count())
    output = StringIO()
    call_command("profile_orm", stdout=output)
    assert "без оптимизации 10, select_related 1, annotate/values 1" in output.getvalue()
    assert "без оптимизации 3, select_related 1" in output.getvalue()
    assert (Event.objects.count(), Registration.objects.count()) == before


def test_analyze_existing_rows_is_read_only(orm_database):
    Registration.objects.create(event_id=1, participant_id=1, registration_date=date(2026, 11, 18))
    before = list(Registration.objects.values())
    output = StringIO()
    call_command("analyze_orm", stdout=output)
    assert "без оптимизации 4, select_related 1, annotate/values 1" in output.getvalue()
    assert "SQL списка:" in output.getvalue()
    assert list(Registration.objects.values()) == before


def test_debug_toolbar_really_records_local_request(tmp_path):
    root = Path(__file__).resolve().parents[1]
    script = "from django.core.management import call_command; call_command('migrate', verbosity=0); call_command('import_pr7'); call_command('analyze_orm', toolbar=True)"
    result = subprocess.run([sys.executable, "-B", "manage.py", "shell", "--command", script], cwd=root,
                            env={**os.environ, "DJANGO_DEBUG_TOOLBAR": "1", "DJANGO_DEBUG": "1",
                                 "DJANGO_DB_FILE": str(tmp_path / "toolbar.sqlite3"), "PYTHONIOENCODING": "utf-8"},
                            capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "DDT: HTTP 200; SQL-панель записала" in result.stdout
