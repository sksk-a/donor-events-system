from django.db import models

from app.models.enums import BloodType
from homepage.models import ContactInfo


class Participant(ContactInfo):
    full_name = models.CharField("ФИО", max_length=200)
    birth_date = models.DateField("Дата рождения")
    blood_type = models.CharField("Группа крови", max_length=3, choices=[(s.value, s.value) for s in BloodType])
    active = models.BooleanField("Активен", default=True)

    class Meta:
        ordering = ("full_name", "id")
        constraints = [models.CheckConstraint(condition=models.Q(blood_type__in=[s.value for s in BloodType]), name="valid_blood_type")]
        verbose_name = "участник"
        verbose_name_plural = "участники"

    def __str__(self):
        return self.full_name
