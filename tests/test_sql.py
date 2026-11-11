"""ПР7: ограничения, транзакции, SQL-выборки и фактическое отображение SQLite."""
import json
import sqlite3

import pytest
from django.test import override_settings

from db.database import connection, fetch_all, fetch_one, queries
from db.import_json import import_data
from tests.conftest import SOURCE


@pytest.fixture
def populated(sql_database, tmp_path):
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    original = data["events"][0]
    data["events"] = [
        {**original, "max_participants": 2},
        {**original, "id": 2, "organization_id": 2, "title": "Полная акция", "status": "OPEN", "max_participants": 1},
        {**original, "id": 3, "title": "Отменённая акция", "status": "CANCELLED"},
        {**original, "id": 4, "title": "Завершённая акция", "status": "COMPLETED"},
        {**original, "id": 5, "title": "Другой день", "event_date": "2026-10-16"},
        {**original, "id": 6, "title": "Без регистраций", "max_participants": 3},
    ]
    data["registrations"] = [
        {"id": i, "participant_id": participant, "event_id": event,
         "status": status, "registration_date": "2026-10-01"}
        for i, participant, event, status in [
            (1, 1, 1, "CONFIRMED"), (2, 2, 1, "CANCELLED"),
            (3, 1, 2, "REGISTERED"), (4, 2, 4, "ATTENDED"), (5, 1, 3, "REGISTERED"),
        ]
    ]
    source = tmp_path / "fixture.json"
    source.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    import_data(source, sql_database)
    return data


def test_original_import_counts_and_repeat(sql_database):
    counts = import_data(SOURCE, sql_database)
    assert counts == {"organizations": 2, "participants": 2, "events": 1, "registrations": 0}
    assert fetch_one("event_totals")["total"] == 1
    with connection() as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert isinstance(conn.execute("SELECT * FROM events").fetchone(), sqlite3.Row)


def test_failed_import_rolls_back_all_rows(sql_database, tmp_path):
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    data["events"][0]["organization_id"] = 999
    source = tmp_path / "invalid.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(sqlite3.IntegrityError):
        import_data(source, sql_database)
    assert fetch_one("event_detail", (1,))["organization_id"] == 1
    assert len(fetch_all("organizations_list")) == 2


def test_constraints(sql_database):
    with connection() as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE events SET max_participants = 0")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE events SET status = 'INVALID'")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO registrations VALUES (1, 999, 1, '2026-10-01', 'REGISTERED', NULL)")


def test_available_sql_handles_capacity_cancelled_and_dates(populated):
    rows = fetch_all("available_events", ("2026-10-15", "", "", 1))
    assert [(r["id"], r["free_places"]) for r in rows] == [(6, 3), (1, 1)]
    assert len(fetch_all("available_events", ("2026-10-15", "Москва", "Москва", 2))) == 1
    assert fetch_all("available_events", ("2026-10-15", "Казань", "Казань", 1)) == []
    assert fetch_all("available_events", ("2026-10-17", "", "", 1)) == []


def test_joins_and_groups_include_zero_counts(populated):
    assert [r["id"] for r in fetch_all("active_registrations")] == [1, 3]
    related = fetch_all("registrations_related")
    assert related[0]["participant_name"] == "Иванов Иван Иванович"
    assert related[0]["organization_name"] == "Красный Крест"
    assert dict(fetch_one("registration_totals")) == {"total": 5, "occupied": 4}
    assert fetch_one("event_totals")["total"] == 6
    by_event = {r["id"]: (r["total"], r["occupied"]) for r in fetch_all("registrations_by_event")}
    assert by_event[1] == (2, 1)
    assert by_event[6] == (0, 0)
    assert [r["total"] for r in fetch_all("events_by_organization")] == [5, 1]
    assert len(fetch_all("popular_events", (0,))) == 4
    assert fetch_all("popular_events", (1,)) == []


def test_all_documented_queries_execute(populated):
    parameters = {
        "events_capacity": (1,), "available_events": ("2026-10-15", "", "", 1),
        "popular_events": (0,), "event_detail": (1,), "organization_detail": (1,),
        "participant_detail": (1,), "registration_detail": (1,),
        "organization_events": (1,), "occupied_places": (1,),
    }
    assert len(queries()) >= 10
    for name in queries():
        fetch_all(name, parameters.get(name, ()))


@pytest.mark.parametrize("url", [
    "/events/available/", "/registrations/active/", "/registrations/statistics/", "/organizations/events/",
])
def test_new_pages(client, url):
    assert client.get(url).status_code == 200


def test_user_search_validation_and_injection(client, populated):
    url = "/events/available/"
    text = client.get(url, {"date": "2026-10-15", "places": 1}).content.decode()
    assert "Без регистраций" in text and "День донора 2026" in text
    assert "Полная акция" not in text and "Отменённая акция" not in text
    for params in [{"date": "wrong", "places": 1}, {"date": "2026-10-15", "places": 0}]:
        response = client.get(url, params)
        assert response.status_code == 200 and 'class="errorlist"' in response.content.decode()
    text = client.get(url, {"date": "2026-10-15", "places": 1, "city": "' OR 1=1 --"}).content.decode()
    assert "По выбранным условиям" in text
    assert fetch_one("event_totals")["total"] == 6


def test_pages_show_sqlite_changes_without_reading_json(client, populated):
    with connection() as conn:
        conn.execute("UPDATE events SET title = 'Изменено в SQLite' WHERE id = 1")
        conn.commit()
    with override_settings(JSON_DATA_FILE="missing-file.json"):
        assert "Изменено в SQLite" in client.get("/events/").content.decode()
        active = client.get("/registrations/active/").content.decode()
        assert "Иванов Иван Иванович" in active and "Изменено в SQLite" in active
        text = client.get("/organizations/events/").content.decode()
        assert "Изменено в SQLite" in text and "Красный Крест" in text
        text = client.get("/registrations/statistics/").content.decode()
        assert "Регистраций: 5" in text and "Изменено в SQLite" in text


def test_capacity_filter_and_having_ui(client, populated):
    text = client.get("/events/", {"capacity": 3}).content.decode()
    assert "Полная акция" not in text and "Без регистраций" in text
    text = client.get("/registrations/statistics/", {"threshold": 1}).content.decode()
    assert "Подходящих мероприятий нет" in text
    assert 'class="errorlist"' in client.get("/registrations/statistics/", {"threshold": -1}).content.decode()


def test_empty_aggregates(sql_database, tmp_path):
    source = tmp_path / "empty.json"
    source.write_text("{}", encoding="utf-8")
    import_data(source, sql_database)
    assert dict(fetch_one("registration_totals")) == {"total": 0, "occupied": 0}
    assert all(value == 0 for value in fetch_one("event_totals"))


def test_missing_database_is_not_created(tmp_path):
    target = tmp_path / "missing.sqlite"
    with pytest.raises(sqlite3.OperationalError), connection(target):
        pass
    assert not target.exists()
