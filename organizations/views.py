from django.shortcuts import render

from app.models import Event, Organization
from db.catalog import get_model, list_models
from db.database import fetch_all


def list_view(request):
    context = {"items": list_models("organizations_list", Organization)}
    return render(request, "organizations/list.html", context)


def detail(request, entity_id):
    item = get_model("organization_detail", Organization, entity_id)
    context = {"item": item}

    context["events"] = list_models("organization_events", Event, (item.id,)) if item else []

    return render(
        request, "organizations/detail.html", context,
        status=404 if item is None else 200,
    )


def event_directory(request):
    return render(request, "organizations/event_directory.html", {
        "items": fetch_all("events_organizations"),
    })
