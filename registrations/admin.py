from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "participant", "registration_date", "status")
    list_display_links = ("id",)
    search_fields = ("event__title", "participant__full_name", "event__organization__name")
    list_filter = ("status", "registration_date", "event", "participant")
    ordering = ("-registration_date", "id")
    list_per_page = 20
    list_select_related = ("event__organization", "participant")
    autocomplete_fields = ("event", "participant")
    date_hierarchy = "registration_date"
    actions = ("cancel_selected",)

    @admin.action(description="Отменить выбранные регистрации", permissions=["change"])
    def cancel_selected(self, request, queryset):
        count = queryset.exclude(status=Registration.Status.CANCELLED).update(status=Registration.Status.CANCELLED)
        self.message_user(request, f"Отменено регистраций: {count}")
