from django.shortcuts import render

from app.models import Event, Organization, Participant, Registration
from db.catalog import list_models


def index(request):
    context = {
        "events": list_models("events_list", Event),
        "organizations": list_models("organizations_list", Organization),
        "participants": list_models("participants_list", Participant),
        "registrations": list_models("registrations_list", Registration),
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(request, "404.html", {}, status=404)
