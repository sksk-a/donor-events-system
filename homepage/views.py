from django.shortcuts import render

from app.utils.web_data import load_catalog


def index(request):
    catalog = load_catalog()
    context = {
        "events": catalog.events,
        "organizations": catalog.organizations,
        "participants": catalog.participants,
        "registrations": catalog.registrations,
    }
    return render(request, "homepage/index.html", context)


def page_not_found(request, exception):
    return render(request, "404.html", {}, status=404)
