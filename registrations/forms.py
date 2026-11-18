from django import forms

from events.models import Event
from participants.models import Participant

SORT_FIELDS = {
    "date": ("registration_date", "id"),
    "newest": ("-registration_date", "id"),
    "event": ("event__title", "registration_date", "id"),
    "participant": ("participant__full_name", "registration_date", "id"),
}


class RegistrationFilterForm(forms.Form):
    date = forms.DateField(label="Дата регистрации", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    event = forms.ModelChoiceField(label="Мероприятие", queryset=Event.objects.none(), required=False)
    participant = forms.ModelChoiceField(label="Участник", queryset=Participant.objects.none(), required=False)
    city = forms.CharField(label="Город мероприятия", max_length=100, required=False)
    q = forms.CharField(label="Участник или название мероприятия", max_length=200, required=False)
    sort = forms.ChoiceField(label="Сортировка", required=False, choices=[
        ("date", "По дате"), ("newest", "Сначала новые"), ("event", "По мероприятию"), ("participant", "По участнику"),
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = Event.objects.order_by("title", "id")
        self.fields["participant"].queryset = Participant.objects.order_by("full_name", "id")


class StatisticsForm(forms.Form):
    threshold = forms.IntegerField(label="Регистраций больше чем", min_value=0, max_value=1000000, required=False)
