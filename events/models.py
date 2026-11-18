from django.core.validators import MinValueValidator
from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Запланировано"
        OPEN = "OPEN", "Открыто"
        COMPLETED = "COMPLETED", "Завершено"
        CANCELLED = "CANCELLED", "Отменено"

    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT, related_name="events")
    title = models.CharField("Название", max_length=200)
    event_date = models.DateField("Дата", db_index=True)
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=250)
    max_participants = models.PositiveIntegerField("Вместимость", validators=[MinValueValidator(1)])
    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.PLANNED)
    description = models.TextField("Описание", blank=True, null=True)
    participants = models.ManyToManyField("participants.Participant", through="registrations.Registration", related_name="events")

    class Meta:
        ordering = ("event_date", "id")
        constraints = [
            models.CheckConstraint(condition=models.Q(max_participants__gt=0), name="positive_event_capacity"),
            models.CheckConstraint(condition=models.Q(status__in=["PLANNED", "OPEN", "COMPLETED", "CANCELLED"]), name="valid_event_status"),
        ]
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"

    def __str__(self):
        return self.title
