from django.db import models


class ContactInfo(models.Model):
    """Общие поля контактов; отдельная таблица для абстрактной модели не создаётся."""
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("Email", blank=True, null=True)

    class Meta:
        abstract = True
