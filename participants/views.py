from django.shortcuts import render

from app.models import Participant
from db.catalog import get_model, list_models


def list_view(request):
    context = {"items": list_models("participants_list", Participant)}
    return render(request, "participants/list.html", context)


def detail(request, entity_id):
    item = get_model("participant_detail", Participant, entity_id)
    context = {"item": item}

    return render(
        request, "participants/detail.html", context,
        status=404 if item is None else 200,
    )
