from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.domain.exceptions import ProductNotFoundError
from apps.catalog.infrastructure.repositories import DjangoProductRepository
from apps.orders.api.serializers import (
    CreateOrderRequestSerializer,
    OrderSerializer,
)
from apps.orders.application.services import OrderService
from apps.orders.domain.exceptions import InsufficientStockError
from apps.orders.infrastructure.notifier import (
    CompositeNotifier,
    RedisStreamNotifier,
    ThreadedLogNotifier,
)
from apps.orders.infrastructure.repositories import DjangoOrderRepository


def _build_notifier():
    if settings.REDIS_URL:
        return CompositeNotifier(
            ThreadedLogNotifier(), RedisStreamNotifier(settings.REDIS_URL)
        )
    return ThreadedLogNotifier()


def _build_order_service() -> OrderService:
    return OrderService(
        order_repository=DjangoOrderRepository(),
        product_repository=DjangoProductRepository(),
        notifier=_build_notifier(),
    )


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        service = _build_order_service()
        try:
            order = service.create_order(
                user_id=request.user.id, **serializer.validated_data
            )
        except ProductNotFoundError:
            return Response(
                {"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
        except InsufficientStockError:
            return Response(
                {"error": "Stock insuficiente"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                "message": "Orden creada con éxito",
                "order_id": order.id,
                "total": order.total,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = _build_order_service()
        if request.user.role == "admin":
            orders = service.list_orders()
        else:
            orders = service.list_orders_by_user(request.user.id)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
