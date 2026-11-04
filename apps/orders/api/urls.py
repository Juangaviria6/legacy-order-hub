from django.urls import path

from apps.orders.api.views import CreateOrderView, OrderListView

urlpatterns = [
    path("create_order", CreateOrderView.as_view(), name="create_order"),
    path(
        "get_all_orders_legacy", OrderListView.as_view(), name="get_all_orders_legacy"
    ),
]
