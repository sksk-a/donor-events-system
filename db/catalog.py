"""Преобразование именованных SQL-строк в прежние dataclass для шаблонов ПР6."""
from dataclasses import fields
from datetime import date

from app.models import BloodType, Event, EventStatus, Participant, Registration, RegistrationStatus
from db.database import fetch_all, fetch_one


def to_model(model, row):
    if row is None:
        return None
    values = {field.name: row[field.name] for field in fields(model)}
    for name in ("event_date", "birth_date", "registration_date"):
        if name in values:
            values[name] = date.fromisoformat(values[name])
    if model is Event:
        values["status"] = EventStatus(values["status"])
    elif model is Registration:
        values["status"] = RegistrationStatus(values["status"])
    elif model is Participant:
        values["blood_type"] = BloodType(values["blood_type"])
        values["active"] = bool(values["active"])
    return model(**values)


def list_models(name, model, params=()):
    return [to_model(model, row) for row in fetch_all(name, params)]


def get_model(name, model, identifier):
    return to_model(model, fetch_one(name, (identifier,)))


def free_places(event):
    occupied = fetch_one("occupied_places", (event.id,))["total"]
    return max(0, event.max_participants - occupied)
