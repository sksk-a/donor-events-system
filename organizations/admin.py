from django.contrib import admin

from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "phone", "email")
    list_display_links = ("name",)
    search_fields = ("name", "city", "email")
    list_filter = ("city",)
    ordering = ("name", "id")
    list_per_page = 20
