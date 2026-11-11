from django.urls import path

from . import views

app_name = "registrations"
urlpatterns = [
    path("", views.list_view, name="list"),
    path("active/", views.active, name="active"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:entity_id>/", views.detail, name="detail"),
]
