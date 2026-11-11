"""Изолированные SQLite-базы: тесты никогда не изменяют рабочие данные сайта."""
import os
from pathlib import Path

import django
import pytest
from django.test import Client, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "donor_site.settings")
django.setup()

from db.import_json import import_data  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1] / "data" / "sample_data.json"


@pytest.fixture
def sql_database(tmp_path):
    target = tmp_path / "test.sqlite"
    import_data(SOURCE, target)
    with override_settings(DONOR_SQLITE_FILE=target):
        yield target


@pytest.fixture
def client(sql_database):
    with override_settings(ALLOWED_HOSTS=["testserver"], DEBUG=False):
        yield Client()
