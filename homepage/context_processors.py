from events.models import Event


def site_context(request):
    return {"site_name": "Донорские мероприятия", "events_count": Event.objects.count()}
