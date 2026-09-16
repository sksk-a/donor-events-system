import os
from contextlib import contextmanager
from collections.abc import Iterator
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from app.exceptions import DatabaseError

load_dotenv()


class Database:
    """Creates PostgreSQL connections; repositories own cursors and SQL."""

    def __init__(self) -> None:
        self._config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "dbname": os.getenv("DB_NAME", "donor_events"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
        }

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        connection = None
        try:
            connection = psycopg.connect(**self._config, row_factory=dict_row)
            yield connection
        except psycopg.Error as exc:
            if connection is not None:
                connection.rollback()
            raise DatabaseError(f"Ошибка PostgreSQL: {exc}") from exc
        finally:
            if connection is not None:
                connection.close()

    def test_connection(self) -> None:
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1")
