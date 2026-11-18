from django.db import models

from homepage.models import ContactInfo


class Organization(ContactInfo):
    name = models.CharField("Название", max_length=200)
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=250)

    class Meta:
        ordering = ("name", "id")
        verbose_name = "организация"
        verbose_name_plural = "организации"

    def __str__(self):
        return self.name
