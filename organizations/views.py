from django.shortcuts import render

from app.utils.web_data import find_by_id, load_catalog


def list_view(request):
    catalog = load_catalog()
    context = {"items": catalog.organizations}
    return render(request, "organizations/list.html", context)


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.organizations, entity_id)
    context = {"item": item}

    context["events"] = [
        event for event in catalog.events if item and event.organization_id == item.id
    ]

    return render(
        request, "organizations/detail.html", context,
        status=404 if item is None else 200,
    )
