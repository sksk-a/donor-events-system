from dataclasses import dataclass
from datetime import date
from .enums import BloodType


@dataclass(slots=True)
class Participant:
    full_name: str
    birth_date: date
    phone: str
    email: str | None
    blood_type: BloodType
    active: bool = True
    id: int | None = None
