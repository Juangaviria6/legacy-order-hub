import abc

from apps.orders.domain.entities import Order


class NotificationPort(abc.ABC):
    @abc.abstractmethod
    def order_created(self, order: Order) -> None: ...


class OrderRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def create(
        self, user_id: int, product_id: int, quantity: int, total: float, status: str
    ) -> int: ...

    @abc.abstractmethod
    def list_all(self) -> list[Order]: ...

    @abc.abstractmethod
    def list_by_user(self, user_id: int) -> list[Order]: ...
