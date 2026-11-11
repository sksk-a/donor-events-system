from django import forms


class StatisticsForm(forms.Form):
    threshold = forms.IntegerField(label="Регистраций больше чем", min_value=0, max_value=1000000, required=False)
