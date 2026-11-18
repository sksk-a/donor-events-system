from django import forms
from django.contrib import admin
from django.db import models

from .models import Registration


class RegistrationInline(admin.TabularInline):
    model = Registration
    fields = ("event", "participant", "registration_date", "status", "notes")
    autocomplete_fields = ("event", "participant")
    extra = 0
    show_change_link = True
    formfield_overrides = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 2, "cols": 35})}}
