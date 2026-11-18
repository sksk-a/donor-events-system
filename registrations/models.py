from django.db import models


class Registration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Зарегистрирован"
        CONFIRMED = "CONFIRMED", "Подтверждено"
        ATTENDED = "ATTENDED", "Посетил"
        CANCELLED = "CANCELLED", "Отменено"

    participant = models.ForeignKey("participants.Participant", on_delete=models.PROTECT, related_name="registrations")
    event = models.ForeignKey("events.Event", on_delete=models.PROTECT, related_name="registrations")
    registration_date = models.DateField("Дата регистрации")
    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.REGISTERED)
    notes = models.TextField("Примечания", blank=True, null=True)

    class Meta:
        ordering = ("-registration_date", "id")
        constraints = [
            models.UniqueConstraint(fields=("participant", "event"), name="unique_participant_event"),
            models.CheckConstraint(condition=models.Q(status__in=["REGISTERED", "CONFIRMED", "ATTENDED", "CANCELLED"]), name="valid_registration_status"),
        ]
        verbose_name = "регистрация"
        verbose_name_plural = "регистрации"

    def cancel(self):
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])

    def __str__(self):
        return f"Регистрация №{self.pk}"
