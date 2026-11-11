"""Проверить каждый запрос через Python sqlite3 CLI (Python 3.12+), не меняя БД."""
import os
import subprocess
import sys

from db.database import database_path, queries

# Фиксированные учебные литералы для CLI, не пользовательские значения.
# В приложении вместо этого всегда используются sqlite3.execute(sql, params).
EXAMPLES = {
    "events_capacity": ("30",),
    "available_events": ("'2026-10-15'", "''", "''", "1"),
    "popular_events": ("0",),
    "event_detail": ("1",),
    "organization_detail": ("1",),
    "participant_detail": ("1",),
    "registration_detail": ("1",),
    "organization_events": ("1",),
    "occupied_places": ("1",),
}


def main():
    if sys.version_info < (3, 12):
        raise SystemExit("Для встроенного SQLite CLI нужен Python 3.12+.")
    target = database_path()
    if not target.is_file():
        raise SystemExit(f"База не найдена: {target}")
    for name, sql in queries().items():
        for literal in EXAMPLES.get(name, ()):
            sql = sql.replace("?", literal, 1)
        result = subprocess.run([sys.executable, "-m", "sqlite3", str(target), sql],
                                capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        if result.returncode:
            raise SystemExit(f"{name}: {result.stderr}")
        print(f"OK {name}: {len(result.stdout.splitlines())} строк")
    print(f"Проверено запросов: {len(queries())}")


if __name__ == "__main__":
    main()
