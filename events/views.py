from datetime import date

from django.shortcuts import render

from app.models import Event, Organization
from db.catalog import free_places, get_model, list_models
from db.database import fetch_all
from .forms import AvailableEventsForm, CapacityForm


def list_view(request):
    form = CapacityForm(request.GET)
    valid = form.is_valid()
    capacity = form.cleaned_data.get("capacity") if valid else None
    items = (list_models("events_capacity", Event, (capacity,)) if capacity is not None
             else list_models("events_list", Event))
    context = {"items": items, "filter_form": form}
    return render(request, "events/list.html", context)


def detail(request, entity_id):
    item = get_model("event_detail", Event, entity_id)
    context = {"item": item}

    context["organization"] = (
        get_model("organization_detail", Organization, item.organization_id) if item else None
    )
    context["free_places"] = free_places(item) if item else 0

    return render(
        request, "events/detail.html", context,
        status=404 if item is None else 200,
    )


def available(request):
    form = AvailableEventsForm(request.GET or None)
    items = []
    searched = form.is_bound and form.is_valid()
    if searched:
        values = form.cleaned_data
        city = values["city"]
        rows = fetch_all("available_events", (
            values["date"].isoformat(), city, city, values["places"],
        ))
        # sqlite3.Row: шаблон обращается к полям по именам.
        items = [dict(row, event_date=date.fromisoformat(row["event_date"])) for row in rows]
    return render(request, "events/available.html", {
        "form": form, "items": items, "searched": searched,
    })
