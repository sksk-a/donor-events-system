from django.shortcuts import render

from app.utils.web_data import find_by_id, load_catalog


def list_view(request):
    catalog = load_catalog()
    context = {"items": catalog.participants}
    return render(request, "participants/list.html", context)


def detail(request, entity_id):
    catalog = load_catalog()
    item = find_by_id(catalog.participants, entity_id)
    context = {"item": item}

    return render(
        request, "participants/detail.html", context,
        status=404 if item is None else 200,
    )
