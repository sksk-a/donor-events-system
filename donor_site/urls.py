from django.urls import include, path

urlpatterns = [
    path("", include("homepage.urls")),
    path("events/", include("events.urls")),
    path("organizations/", include("organizations.urls")),
    path("participants/", include("participants.urls")),
    path("registrations/", include("registrations.urls")),
]

handler404 = "homepage.views.page_not_found"
