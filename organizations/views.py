from django.shortcuts import get_object_or_404, render

from events.models import Event
from .models import Organization


def list_view(request):
    return render(request, "organizations/list.html", {"items": Organization.objects.order_by("name", "id")})


def detail(request, entity_id):
    item = get_object_or_404(Organization, pk=entity_id)
    return render(request, "organizations/detail.html", {
        "item": item, "events": item.events.order_by("event_date", "id"),
    })


def event_directory(request):
    return render(request, "organizations/event_directory.html", {
        "items": Event.objects.select_related("organization").order_by("organization__name", "event_date", "id"),
    })
