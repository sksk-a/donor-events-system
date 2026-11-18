import sqlite3

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError

from db.import_sqlite_to_orm import MODELS, transfer


class Command(BaseCommand):
    help = "Перенести записи ПР7 в ORM с сохранением ID; существующие ID обновляются, лишние записи не удаляются."

    def add_arguments(self, parser):
        parser.add_argument("--source", help="Путь к исходной SQLite ПР7")

    def handle(self, *args, **options):
        try:
            counts = transfer(options["source"])
        except (sqlite3.Error, DatabaseError, ValidationError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        for table, model in MODELS:
            self.stdout.write(f"{table}: источник {counts[table]}, всего ORM {model.objects.count()}")
        self.stdout.write(self.style.SUCCESS("Перенос завершён. Исходная SQLite сохранена."))
