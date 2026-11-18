from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.shortcuts import get_object_or_404, render

from events.models import Event
from organizations.models import Organization
from .forms import RegistrationFilterForm, SORT_FIELDS, StatisticsForm
from .models import Registration


def _list(request, active_only=False):
    params = request.GET.copy()
    if params.get("sort") not in SORT_FIELDS:
        params["sort"] = "date"
    form = RegistrationFilterForm(params)
    items = Registration.objects.all()
    if active_only:
        items = items.active()
    if form.is_valid():
        values = form.cleaned_data
        if values["date"]:
            items = items.for_date(values["date"])
        if values["event"]:
            items = items.filter(event=values["event"])
        if values["participant"]:
            items = items.filter(participant=values["participant"])
        if values["city"]:
            items = items.filter(event__city=values["city"])
        if values["q"]:
            items = items.filter(Q(participant__full_name__icontains=values["q"]) | Q(event__title__icontains=values["q"]))
        items = items.order_by(*SORT_FIELDS[values["sort"] or "date"])
    else:
        items = items.none().order_by("id")
    page_obj = Paginator(items.for_listing(), 5).get_page(request.GET.get("page"))
    return render(request, "registrations/list.html", {
        "items": page_obj, "page_obj": page_obj, "filter_form": form, "active_only": active_only,
    })


def list_view(request):
    return _list(request)


def active(request):
    return _list(request, active_only=True)


def detail(request, entity_id):
    item = get_object_or_404(Registration.objects.select_related("event", "participant"), pk=entity_id)
    return render(request, "registrations/detail.html", {"item": item, "event": item.event, "participant": item.participant})


def statistics(request):
    form = StatisticsForm(request.GET)
    valid = form.is_valid()
    threshold = (form.cleaned_data["threshold"] or 0) if valid else 0
    return render(request, "registrations/statistics.html", {
        "form": form,
        "registration_totals": Registration.objects.aggregate(
            total=Count("id"), occupied=Count("id", filter=~Q(status="CANCELLED")),
            active=Count("id", filter=Q(status__in=[Registration.Status.REGISTERED, Registration.Status.CONFIRMED], event__status__in=[Event.Status.PLANNED, Event.Status.OPEN])),
            cancelled=Count("id", filter=Q(status=Registration.Status.CANCELLED)),
            completed=Count("id", filter=Q(status=Registration.Status.ATTENDED)),
        ),
        "event_totals": Event.objects.aggregate(
            total=Count("id"), capacity=Sum("max_participants", default=0),
            average_capacity=Avg("max_participants", default=0),
            min_capacity=Min("max_participants", default=0), max_capacity=Max("max_participants", default=0),
        ),
        "by_event": Event.objects.annotate(
            total=Count("registrations"), occupied=Count("registrations", filter=~Q(registrations__status="CANCELLED")),
        ).order_by("-total", "id"),
        "by_organization": Organization.objects.annotate(total=Count("events")).order_by("-total", "id"),
        "popular": Event.objects.annotate(total=Count("registrations", filter=~Q(registrations__status="CANCELLED"))).filter(
            total__gt=threshold,
        ).order_by("-total", "id") if valid else Event.objects.none(),
    })
