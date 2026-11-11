"""Транзакционный перенос исходного JSON; повторный импорт не дублирует записи."""
import argparse
import json

from db.database import BASE_DIR, DEFAULT_DATABASE, connection

# Только внутренние константы; пользовательский ввод не становится SQL-кодом.
INSERTS = {
    "organizations": "INSERT INTO organizations (id,name,city,address,phone,email) VALUES (?,?,?,?,?,?)",
    "participants": "INSERT INTO participants (id,full_name,birth_date,phone,email,blood_type,active) VALUES (?,?,?,?,?,?,?)",
    "events": "INSERT INTO events (id,organization_id,title,event_date,city,address,max_participants,status,description) VALUES (?,?,?,?,?,?,?,?,?)",
    "registrations": "INSERT INTO registrations (id,participant_id,event_id,registration_date,status,notes) VALUES (?,?,?,?,?,?)",
}
FIELDS = {
    "organizations": ("id", "name", "city", "address", "phone", "email"),
    "participants": ("id", "full_name", "birth_date", "phone", "email", "blood_type", "active"),
    "events": ("id", "organization_id", "title", "event_date", "city", "address", "max_participants", "status", "description"),
    "registrations": ("id", "participant_id", "event_id", "registration_date", "status", "notes"),
}
DEFAULTS = {"participants": {"active": True}, "events": {"status": "PLANNED"},
            "registrations": {"status": "REGISTERED"}}


def import_data(source=BASE_DIR / "data" / "sample_data.json", target=DEFAULT_DATABASE):
    with open(source, encoding="utf-8") as stream:
        data = json.load(stream)
    with connection(target, create=True) as conn:
        conn.executescript((BASE_DIR / "sql" / "schema.sql").read_text(encoding="utf-8"))
        try:
            # Удаление и вставка вместе: ошибка внешнего ключа возвращает старые данные.
            conn.execute("BEGIN")
            conn.execute("DELETE FROM registrations")
            conn.execute("DELETE FROM events")
            conn.execute("DELETE FROM participants")
            conn.execute("DELETE FROM organizations")
            counts = {}
            for table, fields in FIELDS.items():
                rows = [{**DEFAULTS.get(table, {}), **row} for row in data.get(table, [])]
                conn.executemany(INSERTS[table], [tuple(row.get(field) for field in fields) for row in rows])
                counts[table] = len(rows)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    return counts


def main():
    parser = argparse.ArgumentParser(description="Заменить данные SQLite содержимым JSON (сначала сохраните свою БД).")
    parser.add_argument("--source", default=str(BASE_DIR / "data" / "sample_data.json"))
    parser.add_argument("--database", default=str(DEFAULT_DATABASE))
    args = parser.parse_args()
    counts = import_data(args.source, args.database)
    print(f"База: {args.database}")
    for table, count in counts.items():
        print(f"{table}: {count}")


if __name__ == "__main__":
    main()
