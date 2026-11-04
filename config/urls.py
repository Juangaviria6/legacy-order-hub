from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from common.observability.views import healthcheck

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("healthcheck", healthcheck, name="healthcheck"),
    path("", include("django_prometheus.urls")),
    path("", include("apps.users.api.urls")),
    path("", include("apps.catalog.api.urls")),
    path("", include("apps.orders.api.urls")),
]
