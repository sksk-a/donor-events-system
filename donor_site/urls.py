from django.conf import settings
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Управление донорскими мероприятиями"
admin.site.site_title = "Донорские мероприятия"
admin.site.index_title = "Администрирование"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("events/", include("events.urls")),
    path("organizations/", include("organizations.urls")),
    path("participants/", include("participants.urls")),
    path("registrations/", include("registrations.urls")),
]

if settings.DEBUG_TOOLBAR_ENABLED:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]

handler404 = "homepage.views.page_not_found"
