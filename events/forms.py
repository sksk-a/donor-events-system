from django import forms


class CapacityForm(forms.Form):
    capacity = forms.IntegerField(label="Вместимость от", min_value=1, max_value=1000000, required=False)


class AvailableEventsForm(forms.Form):
    date = forms.DateField(label="Дата мероприятия", widget=forms.DateInput(attrs={"type": "date"}))
    places = forms.IntegerField(label="Свободных мест не меньше", min_value=1, max_value=1000000, initial=1)
    city = forms.CharField(label="Город", max_length=100, required=False)
