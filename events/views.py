from django.shortcuts import get_object_or_404, render

from .forms import AvailableEventsForm, CapacityForm
from .models import Event
from .querysets import with_free_places


def list_view(request):
    form = CapacityForm(request.GET)
    items = Event.objects.all().order_by("event_date", "id")
    if form.is_valid():
        values = form.cleaned_data
        if values["capacity"] is not None:
            items = items.filter(max_participants__gte=values["capacity"])
        if values["q"]:
            items = items.filter(title__icontains=values["q"])
    else:
        items = items.none()
    return render(request, "events/list.html", {"items": items, "filter_form": form})


def detail(request, entity_id=None, slug=None):
    lookup = {"slug": slug} if slug is not None else {"pk": entity_id}
    item = get_object_or_404(with_free_places(), **lookup)
    return render(request, "events/detail.html", {
        "item": item, "organization": item.organization, "free_places": max(0, item.free_places),
    })


def available(request):
    form = AvailableEventsForm(request.GET or None)
    items = Event.objects.none()
    searched = form.is_bound and form.is_valid()
    if searched:
        values = form.cleaned_data
        items = with_free_places().filter(
            event_date=values["date"], status__in=[Event.Status.PLANNED, Event.Status.OPEN],
            free_places__gte=values["places"],
        )
        if values["city"]:
            items = items.filter(city=values["city"])
        items = items.order_by("-free_places", "id")
    return render(request, "events/available.html", {"form": form, "items": items, "searched": searched})
