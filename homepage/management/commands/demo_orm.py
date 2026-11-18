from django.core.management.base import BaseCommand
from django.db import transaction

from organizations.models import Organization


class Command(BaseCommand):
    help = "Демонстрация CRUD через ORM; все изменения откатываются."

    def handle(self, *args, **options):
        with transaction.atomic():
            item = Organization.objects.create(name="Учебная организация", city="Москва", address="Учебный адрес", phone="+70000000000")
            self.stdout.write(f"CREATE: id={item.pk}")
            item = Organization.objects.get(pk=item.pk)
            self.stdout.write(f"READ: {item.name}")
            item.name = "Обновлённая учебная организация"
            item.save(update_fields=["name"])
            self.stdout.write(f"UPDATE: {item.name}")
            item.delete()
            self.stdout.write("DELETE: выполнено")
            transaction.set_rollback(True)
        self.stdout.write("CRUD проверен; рабочие данные не изменены.")
