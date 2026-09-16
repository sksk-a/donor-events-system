from dataclasses import dataclass
from datetime import date
from .enums import EventStatus


@dataclass(slots=True)
class Event:
    organization_id: int
    title: str
    event_date: date
    city: str
    address: str
    max_participants: int
    status: EventStatus = EventStatus.PLANNED
    description: str | None = None
    id: int | None = None
