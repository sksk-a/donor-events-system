from dataclasses import dataclass
from datetime import date
from .enums import RegistrationStatus


@dataclass(slots=True)
class Registration:
    participant_id: int
    event_id: int
    registration_date: date
    status: RegistrationStatus = RegistrationStatus.REGISTERED
    notes: str | None = None
    id: int | None = None


@dataclass(slots=True)
class RegistrationView:
    id: int
    participant_id: int
    participant_name: str
    event_id: int
    event_title: str
    organization_name: str
    event_date: date
    city: str
    registration_date: date
    status: RegistrationStatus
    event_status: str
    notes: str | None
