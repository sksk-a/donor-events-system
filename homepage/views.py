from django.shortcuts import render

from events.models import Event
from organizations.models import Organization
from participants.models import Participant
from registrations.models import Registration


def index(request):
    return render(request, "homepage/index.html", {
        "events": Event.objects.all(), "organizations": Organization.objects.all(),
        "participants": Participant.objects.all(), "registrations": Registration.objects.all(),
    })


def page_not_found(request, exception):
    return render(request, "404.html", {}, status=404)
