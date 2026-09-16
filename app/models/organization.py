from dataclasses import dataclass


@dataclass(slots=True)
class Organization:
    name: str
    city: str
    address: str
    phone: str
    email: str | None = None
    id: int | None = None
