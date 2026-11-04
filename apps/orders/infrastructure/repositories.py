from apps.orders.domain.entities import Order
from apps.orders.domain.ports import OrderRepositoryPort
from apps.orders.models import OrderModel


class DjangoOrderRepository(OrderRepositoryPort):
    def create(
        self, user_id: int, product_id: int, quantity: int, total: float, status: str
    ) -> int:
        row = OrderModel.objects.create(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total=total,
            status=status,
        )
        return row.id

    def list_all(self) -> list[Order]:
        return self._to_entities(OrderModel.objects.all())

    def list_by_user(self, user_id: int) -> list[Order]:
        return self._to_entities(OrderModel.objects.filter(user_id=user_id))

    @staticmethod
    def _to_entities(rows) -> list[Order]:
        return [
            Order(
                id=row.id,
                user_id=row.user_id,
                product_id=row.product_id,
                quantity=row.quantity,
                total=row.total,
                status=row.status,
            )
            for row in rows
        ]
