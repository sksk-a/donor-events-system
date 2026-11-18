from django.db.models import Count, F, Q

from .models import Event


def with_free_places():
    return Event.objects.select_related("organization").annotate(
        occupied=Count("registrations", filter=~Q(registrations__status="CANCELLED")),
    ).annotate(free_places=F("max_participants") - F("occupied"))
