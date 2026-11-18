from django.contrib import admin

from registrations.admin_inlines import RegistrationInline
from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "blood_type", "active", "phone", "email")
    list_display_links = ("full_name",)
    search_fields = ("full_name", "phone", "email")
    list_filter = ("active", "blood_type")
    ordering = ("full_name", "id")
    list_per_page = 20
    inlines = (RegistrationInline,)
