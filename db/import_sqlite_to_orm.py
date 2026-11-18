"""ПР9: однократное чтение исходной SQLite, запись только средствами ORM."""
import sqlite3
from datetime import date
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection, transaction

from events.models import Event
from organizations.models import Organization
from participants.models import Participant
from registrations.models import Registration

MODELS = (("organizations", Organization), ("participants", Participant),
          ("events", Event), ("registrations", Registration))


def transfer(source=None):
    path = Path(source or settings.DONOR_SQLITE_FILE).resolve()
    if path == Path(connection.settings_dict["NAME"]).resolve():
        raise ValueError("Исходная база ПР7 должна отличаться от целевой базы Django.")
    # URI mode=ro гарантирует, что исходная база не изменится и не создастся при опечатке.
    source_conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    source_conn.row_factory = sqlite3.Row
    try:
        with source_conn:
            if source_conn.execute("PRAGMA foreign_key_check").fetchall():
                raise ValidationError("В исходной базе нарушены внешние ключи.")
            data = {}
            for table, model in MODELS:
                # Имя таблицы — внутренняя константа, не пользовательский параметр.
                data[table] = [dict(row) for row in source_conn.execute(f"SELECT * FROM {table} ORDER BY id")]
        with transaction.atomic():
            for table, model in MODELS:
                for row in data[table]:
                    pk = row.pop("id")
                    for field in ("event_date", "birth_date", "registration_date"):
                        if field in row:
                            row[field] = date.fromisoformat(row[field])
                    if "active" in row:
                        if row["active"] not in (0, 1):
                            raise ValidationError("active должен быть 0 или 1.")
                        row["active"] = bool(row["active"])
                    candidate = model(pk=pk, **row)
                    candidate.full_clean(validate_unique=False, validate_constraints=False)
                    model.objects.update_or_create(pk=pk, defaults=row)
            return {table: len(data[table]) for table, _ in MODELS}
    finally:
        source_conn.close()
