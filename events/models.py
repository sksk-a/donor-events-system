from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from homepage.utils import event_slug


class Event(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Запланировано"
        OPEN = "OPEN", "Открыто"
        COMPLETED = "COMPLETED", "Завершено"
        CANCELLED = "CANCELLED", "Отменено"

    organization = models.ForeignKey("organizations.Organization", on_delete=models.PROTECT, related_name="events", verbose_name="Организация")
    title = models.CharField("Название", max_length=200)
    slug = models.SlugField("Адрес страницы", max_length=220, unique=True, blank=True)
    event_date = models.DateField("Дата", db_index=True)
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=250)
    max_participants = models.PositiveIntegerField("Вместимость", validators=[MinValueValidator(1)])
    is_large = models.GeneratedField(
        expression=models.Case(models.When(max_participants__gte=100, then=models.Value(True)), default=models.Value(False)),
        output_field=models.BooleanField(), db_persist=True, verbose_name="Масштабная акция",
    )
    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.PLANNED)
    description = models.TextField("Описание", blank=True, null=True)
    participants = models.ManyToManyField("participants.Participant", through="registrations.Registration", related_name="events", verbose_name="Участники")

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

    def get_absolute_url(self):
        return reverse("events:detail-slug", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base = event_slug(self.title)
            candidate = f"{base}-{self.pk}" if self.pk else base
            index = 2
            while type(self).objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{index}"
                index += 1
            self.slug = candidate
            if kwargs.get("update_fields") is not None:
                kwargs["update_fields"] = set(kwargs["update_fields"]) | {"slug"}
        super().save(*args, **kwargs)
