from django.shortcuts import render

from app.models import Event, Participant, Registration
from db.catalog import get_model
from db.database import fetch_all, fetch_one
from .forms import StatisticsForm


def list_view(request):
    rows = fetch_all("registrations_related")
    context = {"items": [_display_row(row) for row in rows]}
    return render(request, "registrations/list.html", context)


def detail(request, entity_id):
    item = get_model("registration_detail", Registration, entity_id)
    context = {"item": item}

    context["event"] = (
        get_model("event_detail", Event, item.event_id) if item else None
    )
    context["participant"] = (
        get_model("participant_detail", Participant, item.participant_id) if item else None
    )

    return render(
        request, "registrations/detail.html", context,
        status=404 if item is None else 200,
    )


def _display_row(row):
    from datetime import date
    from app.models import RegistrationStatus

    return dict(row, registration_date=date.fromisoformat(row["registration_date"]),
                status=RegistrationStatus(row["status"]))


def active(request):
    return render(request, "registrations/list.html", {
        "items": [_display_row(row) for row in fetch_all("active_registrations")],
        "active_only": True,
    })


def statistics(request):
    form = StatisticsForm(request.GET)
    valid = form.is_valid()
    threshold = form.cleaned_data.get("threshold") if valid else None
    threshold = 0 if threshold is None else threshold
    return render(request, "registrations/statistics.html", {
        "form": form,
        "registration_totals": fetch_one("registration_totals"),
        "event_totals": fetch_one("event_totals"),
        "by_event": fetch_all("registrations_by_event"),
        "by_organization": fetch_all("events_by_organization"),
        "popular": fetch_all("popular_events", (threshold,)) if valid else [],
    })
