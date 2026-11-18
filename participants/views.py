from django.shortcuts import get_object_or_404, render

from .models import Participant


def list_view(request):
    return render(request, "participants/list.html", {"items": Participant.objects.order_by("full_name", "id")})


def detail(request, entity_id):
    return render(request, "participants/detail.html", {"item": get_object_or_404(Participant, pk=entity_id)})
