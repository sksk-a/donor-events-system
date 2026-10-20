"""Адаптер JSON → существующие dataclass-модели; не обращается к PostgreSQL."""
from dataclasses import dataclass
from datetime import date
from typing import TypeVar

from django.conf import settings

from app.models import (
    BloodType, Event, EventStatus, Organization, Participant,
    Registration, RegistrationStatus,
)
from app.utils.json_handler import JsonHandler

T = TypeVar("T")


def find_by_id(items: list[T], entity_id: int) -> T | None:
    return next((item for item in items if item.id == entity_id), None)


@dataclass
class Catalog:
    organizations: list[Organization]
    events: list[Event]
    participants: list[Participant]
    registrations: list[Registration]

    def free_places(self, event: Event) -> int:
        occupied = sum(
            r.event_id == event.id and r.status != RegistrationStatus.CANCELLED
            for r in self.registrations
        )
        return max(0, event.max_participants - occupied)


def load_catalog() -> Catalog:
    """Читать свежий снимок файла при запросе; ошибки файла не скрывать."""
    data = JsonHandler(str(settings.JSON_DATA_FILE)).read_json()
    organizations = [Organization(**row) for row in data.get("organizations", [])]
    events = [Event(**{
        **row,
        "event_date": date.fromisoformat(row["event_date"]),
        "status": EventStatus(row.get("status", "PLANNED")),
    }) for row in data.get("events", [])]
    participants = [Participant(**{
        **row,
        "birth_date": date.fromisoformat(row["birth_date"]),
        "blood_type": BloodType(row["blood_type"]),
    }) for row in data.get("participants", [])]
    registrations = [Registration(**{
        **row,
        "registration_date": date.fromisoformat(row["registration_date"]),
        "status": RegistrationStatus(row.get("status", "REGISTERED")),
    }) for row in data.get("registrations", [])]
    return Catalog(organizations, events, participants, registrations)
