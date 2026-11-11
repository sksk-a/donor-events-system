"""Подключение и выполнение SQL из единого файла запросов."""
import os
import sqlite3
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = BASE_DIR / "data" / "donor_events.sqlite"


def database_path():
    """Настройка Django переопределяется в тестах; CLI работает и без Django."""
    from django.conf import settings

    if settings.configured:
        path = Path(settings.DONOR_SQLITE_FILE)
    else:
        path = Path(os.environ.get("DONOR_SQLITE_FILE", DEFAULT_DATABASE))
    return path if path.is_absolute() else BASE_DIR / path


def get_connection(path=None, *, create=False):
    target = Path(path) if path is not None else database_path()
    if create:
        target.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(target)
    else:
        # Не создавать незаметно пустую БД при опечатке в пути.
        conn = sqlite3.connect(target.resolve().as_uri() + "?mode=rw", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def connection(path=None, *, create=False):
    conn = get_connection(path, create=create)
    try:
        yield conn
    finally:
        conn.close()


@lru_cache(maxsize=1)
def queries():
    """Именованные запросы исполняются прямо из sql/queries.sql, без копий в views."""
    text = (BASE_DIR / "sql" / "queries.sql").read_text(encoding="utf-8")
    result = {}
    for block in text.split("-- name: ")[1:]:
        name, sql = block.split("\n", 1)
        result[name.strip()] = sql.strip()
    return result


def fetch_all(name, params=()):
    with connection() as conn:
        return conn.execute(queries()[name], params).fetchall()


def fetch_one(name, params=()):
    with connection() as conn:
        return conn.execute(queries()[name], params).fetchone()
