from django.contrib import admin

from registrations.admin_inlines import RegistrationInline
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "organization", "event_date", "city", "max_participants", "is_large", "status")
    list_display_links = ("title",)
    search_fields = ("title", "organization__name", "city")
    list_filter = ("status", "event_date", "city", "organization", "max_participants")
    ordering = ("event_date", "id")
    list_per_page = 20
    list_select_related = ("organization",)
    autocomplete_fields = ("organization",)
    date_hierarchy = "event_date"
    inlines = (RegistrationInline,)
    readonly_fields = ("is_large",)
    prepopulated_fields = {"slug": ("title",)}
