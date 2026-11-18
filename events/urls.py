from django.urls import path

from . import views

app_name = "events"
urlpatterns = [
    path("", views.list_view, name="list"),
    path("available/", views.available, name="available"),
    path("by-slug/<slug:slug>/", views.detail, name="detail-slug"),
    path("<int:entity_id>/", views.detail, name="detail"),
]
