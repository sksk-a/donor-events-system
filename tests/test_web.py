"""HTTP и JSON проверяются без PostgreSQL и без pytest-django."""
import json
import os
from datetime import date
from pathlib import Path

import django
import pytest
from django.test import Client, override_settings
from django.urls import reverse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "donor_site.settings")
django.setup()

from app.models import Event, EventStatus  # noqa: E402
from app.utils.web_data import load_catalog  # noqa: E402


@pytest.fixture
def client():
    with override_settings(ALLOWED_HOSTS=["testserver"], DEBUG=False):
        yield Client()


@pytest.mark.parametrize("path", [
    "/", "/events/", "/events/1/", "/organizations/",
    "/organizations/1/", "/organizations/2/", "/participants/",
    "/participants/1/", "/participants/2/", "/registrations/",
])
def test_existing_pages(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert 'charset="UTF-8"' in response.content.decode()
    assert '<html lang="ru">' in response.content.decode()


@pytest.mark.parametrize("section", [
    "events", "organizations", "participants", "registrations",
])
@pytest.mark.parametrize("identifier", ["99999", "abc"])
def test_missing_objects_and_invalid_converter(client, section, identifier):
    assert client.get(f"/{section}/{identifier}/").status_code == 404


def test_unknown_route_uses_custom_404(client):
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    assert "страница не найдена" in response.content.decode()


def test_catalog_uses_existing_models_and_dates():
    catalog = load_catalog()
    event = catalog.events[0]
    assert isinstance(event, Event)
    assert isinstance(event.event_date, date)
    assert isinstance(event.status, EventStatus)
    assert catalog.free_places(event) == event.max_participants


def test_empty_catalog(client, tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("{}", encoding="utf-8")
    with override_settings(JSON_DATA_FILE=path):
        for section in ("events", "organizations", "participants", "registrations"):
            response = client.get(f"/{section}/")
            assert response.status_code == 200
            assert "Пока нет данных" in response.content.decode()
            assert client.get(f"/{section}/1/").status_code == 404


def test_registration_links_and_cancelled_capacity(client, tmp_path):
    source = Path(__file__).resolve().parents[1] / "data" / "sample_data.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    data["registrations"] = [
        {"id": 1, "participant_id": 1, "event_id": 1,
         "registration_date": "2026-10-01", "status": "CONFIRMED"},
        {"id": 2, "participant_id": 2, "event_id": 1,
         "registration_date": "2026-10-02", "status": "CANCELLED"},
    ]
    path = tmp_path / "registrations.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with override_settings(JSON_DATA_FILE=path):
        catalog = load_catalog()
        assert catalog.free_places(catalog.events[0]) == 49
        for entity_id in (1, 2):
            response = client.get(reverse("registrations:detail", args=[entity_id]))
            assert response.status_code == 200
            text = response.content.decode()
            assert '/events/1/' in text
            assert f'/participants/{entity_id}/' in text
            expected = "Подтверждено" if entity_id == 1 else "Отменено"
            assert expected in text
        assert "Подтверждено" in client.get("/registrations/").content.decode()
        assert "Отменено" in client.get("/registrations/").content.decode()


def test_json_text_is_escaped(client, tmp_path):
    source = Path(__file__).resolve().parents[1] / "data" / "sample_data.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    data["events"][0]["title"] = '<script>alert("x")</script>'
    path = tmp_path / "escaped.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with override_settings(JSON_DATA_FILE=path):
        for url in ("/events/", "/events/1/"):
            text = client.get(url).content.decode()
            assert '<script>alert(' not in text
            assert '&lt;script&gt;' in text


def test_template_date_default_and_related_organization(client, tmp_path):
    source = Path(__file__).resolve().parents[1] / "data" / "sample_data.json"
    data = json.loads(source.read_text(encoding="utf-8"))
    data["events"][0]["description"] = ""
    path = tmp_path / "default.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with override_settings(JSON_DATA_FILE=path):
        response = client.get("/events/1/")
        text = response.content.decode()
        assert "15.10.2026" in text
        assert "Описание пока не добавлено" in text
        assert '/organizations/1/' in text
        assert "Красный Крест" in text


def test_corrupt_json_is_not_disguised_as_empty_list(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")
    with override_settings(JSON_DATA_FILE=path):
        with pytest.raises(json.JSONDecodeError):
            load_catalog()
