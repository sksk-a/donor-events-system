from django.urls import path

from . import views

app_name = "registrations"
urlpatterns = [
    path("", views.list_view, name="list"),
    path("<int:entity_id>/", views.detail, name="detail"),
]
