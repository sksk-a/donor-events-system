from django.shortcuts import render

from app.utils.web_data import find_by_id, load_catalog


def list_view(request):
    catalog = load_catalog()
    context = {"items": catalog.events}
    return render(request, "events/list.html", context)


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.events, entity_id)
    context = {"item": item}

    context["organization"] = (
        find_by_id(catalog.organizations, item.organization_id) if item else None
    )
    context["free_places"] = catalog.free_places(item) if item else 0

    return render(
        request, "events/detail.html", context,
        status=404 if item is None else 200,
    )
