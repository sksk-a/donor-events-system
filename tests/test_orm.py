import hashlib
from datetime import date
from io import StringIO

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test.utils import CaptureQueriesContext
from django.db import connection as django_connection

from db.import_sqlite_to_orm import transfer
from events.models import Event
from events.querysets import with_free_places
from organizations.models import Organization
from participants.models import Participant
from registrations.models import Registration


@pytest.fixture
def many_registrations(orm_database):
    event = Event.objects.get(pk=1)
    for i in range(1, 13):
        participant = Participant.objects.create(full_name=f"Донор {i:02}", birth_date=date(1990, 1, 1), phone="123", blood_type="O+")
        Registration.objects.create(event=event, participant=participant, registration_date=date(2026, 10, 1), status="CONFIRMED")
    return event


def test_transfer_is_repeatable_and_preserves_source(orm_database):
    before = hashlib.sha256(orm_database.read_bytes()).hexdigest()
    assert transfer(orm_database) == {"organizations": 2, "participants": 2, "events": 1, "registrations": 0}
    assert Organization.objects.count() == 2 and Participant.objects.count() == 2
    event = Event.objects.select_related("organization").get(pk=1)
    assert event.organization.name == "Красный Крест" and isinstance(event.event_date, date)
    assert hashlib.sha256(orm_database.read_bytes()).hexdigest() == before


def test_crud_and_protected_relationships(orm_database):
    participant = Participant.objects.get(pk=1)
    event = Event.objects.get(pk=1)
    item = Registration.objects.create(participant=participant, event=event, registration_date=date(2026, 10, 1))
    assert Registration.objects.get(pk=item.pk).participant_id == participant.pk
    assert list(event.participants.all()) == [participant]
    assert event.registrations.get().pk == item.pk
    item.cancel()
    item.refresh_from_db()
    assert item.status == Registration.Status.CANCELLED
    with pytest.raises(ProtectedError):
        event.delete()
    with pytest.raises(ProtectedError):
        participant.delete()
    with pytest.raises(ProtectedError):
        event.organization.delete()
    item.delete()
    assert Registration.objects.count() == 0


def test_constraints_and_validation(orm_database):
    event = Event.objects.get(pk=1)
    event.max_participants = 0
    with pytest.raises(ValidationError):
        event.full_clean()
    with pytest.raises(IntegrityError), transaction.atomic():
        Event.objects.filter(pk=1).update(max_participants=0)
    fields = dict(event_id=1, participant_id=1, registration_date=date(2026, 10, 1))
    Registration.objects.create(**fields)
    with pytest.raises(IntegrityError), transaction.atomic():
        Registration.objects.create(**fields)


def test_import_rollback_on_bad_date(orm_database):
    from db.database import connection
    with connection(orm_database) as conn:
        conn.execute("UPDATE organizations SET name='Не должно сохраниться' WHERE id=1")
        conn.execute("UPDATE events SET event_date='wrong' WHERE id=1")
        conn.commit()
    with pytest.raises(ValueError):
        transfer(orm_database)
    assert Organization.objects.get(pk=1).name == "Красный Крест"


def test_demo_crud_leaves_database_unchanged(orm_database):
    before = list(Organization.objects.values())
    output = StringIO()
    call_command("demo_orm", stdout=output)
    assert "CRUD проверен" in output.getvalue()
    assert list(Organization.objects.values()) == before


def test_pagination_filters_and_parameters(client, many_registrations):
    params = {"date": "2026-10-01", "event": 1, "city": "Москва", "sort": "participant", "q": "Донор"}
    response = client.get("/registrations/", params)
    page = response.context["page_obj"]
    assert page.paginator.count == 12 and len(page) == 5
    text = response.content.decode()
    assert "page=2" in text and "sort=participant" in text and "date=2026-10-01" in text
    second = client.get("/registrations/", {**params, "page": 2}).context["page_obj"]
    assert second.number == 2 and second[0]["participant_name"] == "Донор 06"
    for value, expected in [("abc", 1), (999, 3), (-1, 3)]:
        assert client.get("/registrations/", {**params, "page": value}).context["page_obj"].number == expected
    assert client.get("/registrations/", {**params, "city": "Казань"}).context["page_obj"].paginator.count == 0


@pytest.mark.parametrize("params", [{"date": "wrong"}, {"event": "abc"}, {"event": 9999}, {"participant": -1}])
def test_bad_filters_are_safe(client, many_registrations, params):
    response = client.get("/registrations/", params)
    assert response.status_code == 200 and response.context["filter_form"].errors
    assert response.context["page_obj"].paginator.count == 0


def test_search_sort_exclude_and_orm_only(client, many_registrations, monkeypatch):
    from db import database

    def fail(*args, **kwargs):
        raise AssertionError("Сайт не должен вызывать слой sqlite3 ПР7")
    monkeypatch.setattr(database, "fetch_all", fail)
    monkeypatch.setattr(database, "get_connection", fail)
    Registration.objects.order_by("pk").first().cancel()
    active = client.get("/registrations/active/", {"q": "Донор", "sort": "participant"})
    assert active.context["page_obj"].paginator.count == 11
    assert client.get("/events/", {"q": "День донора"}).context["items"].count() == 1
    assert client.get("/events/", {"q": "Нет такой акции"}).context["items"].count() == 0
    assert client.get("/registrations/", {"q": "День донора"}).context["page_obj"].paginator.count == 12
    assert client.get("/registrations/", {"sort": "DROP TABLE"}).status_code == 200
    for url in ["/", "/events/1/", "/organizations/", "/participants/", "/registrations/statistics/"]:
        assert client.get(url).status_code == 200


def test_related_loading_and_free_places(many_registrations):
    with CaptureQueriesContext(django_connection) as capture:
        rows = list(Registration.objects.select_related("participant", "event__organization"))
        assert all(row.participant.full_name and row.event.organization.name for row in rows)
    assert len(capture) == 1
    assert with_free_places().get(pk=1).free_places == 38
    rows[0].cancel()
    assert with_free_places().get(pk=1).free_places == 39


def test_fixture_dump_load(orm_database, tmp_path):
    output = tmp_path / "fixture.json"
    call_command("dumpdata", "organizations", "participants", "events", "registrations", output=str(output))
    Registration.objects.all().delete()
    Event.objects.all().delete()
    Participant.objects.all().delete()
    Organization.objects.all().delete()
    call_command("loaddata", str(output), verbosity=0)
    assert Event.objects.get(pk=1).organization.name == "Красный Крест"
    assert Participant.objects.count() == 2
