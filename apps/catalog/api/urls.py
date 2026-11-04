from django.urls import path

from apps.catalog.api.views import ProductListCreateView

urlpatterns = [
    path("products", ProductListCreateView.as_view(), name="products"),
]
