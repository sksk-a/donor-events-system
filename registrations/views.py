from django.shortcuts import render

from app.utils.web_data import find_by_id, load_catalog


def list_view(request):
    catalog = load_catalog()
    context = {"items": catalog.registrations}
    return render(request, "registrations/list.html", context)


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.registrations, entity_id)
    context = {"item": item}

    context["event"] = (
        find_by_id(catalog.events, item.event_id) if item else None
    )
    context["participant"] = (
        find_by_id(catalog.participants, item.participant_id) if item else None
    )

    return render(
        request, "registrations/detail.html", context,
        status=404 if item is None else 200,
    )
