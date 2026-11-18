from django.db import models


class RegistrationQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status__in=[self.model.Status.REGISTERED, self.model.Status.CONFIRMED],
                           event__status__in=["PLANNED", "OPEN"])

    def cancelled(self):
        return self.filter(status=self.model.Status.CANCELLED)

    def completed(self):
        return self.filter(status=self.model.Status.ATTENDED)

    def for_date(self, selected_date):
        return self.filter(registration_date=selected_date)

    def occupied(self):
        return self.exclude(status=self.model.Status.CANCELLED)

    def for_listing(self):
        """Один JOIN-запрос и только необходимые для карточек поля."""
        return self.annotate(
            participant_name=models.F("participant__full_name"), event_title=models.F("event__title"),
            organization_name=models.F("event__organization__name"),
        ).values("id", "event_id", "participant_id", "registration_date", "status", "notes",
                 "participant_name", "event_title", "organization_name")


class Registration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = "REGISTERED", "Зарегистрирован"
        CONFIRMED = "CONFIRMED", "Подтверждено"
        ATTENDED = "ATTENDED", "Посетил"
        CANCELLED = "CANCELLED", "Отменено"

    participant = models.ForeignKey("participants.Participant", on_delete=models.PROTECT, related_name="registrations", verbose_name="Участник")
    event = models.ForeignKey("events.Event", on_delete=models.PROTECT, related_name="registrations", verbose_name="Мероприятие")
    registration_date = models.DateField("Дата регистрации")
    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.REGISTERED)
    notes = models.TextField("Примечания", blank=True, null=True)
    objects = RegistrationQuerySet.as_manager()

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
