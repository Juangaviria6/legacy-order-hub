import abc

from apps.catalog.domain.entities import Product


class ProductRepositoryPort(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, product_id: int) -> Product | None: ...

    @abc.abstractmethod
    def get_by_id_for_update(self, product_id: int) -> Product | None: ...

    @abc.abstractmethod
    def create(self, name: str, price: float, stock: int) -> int: ...

    @abc.abstractmethod
    def update_stock(self, product_id: int, new_stock: int) -> None: ...

    @abc.abstractmethod
    def list_all(self) -> list[Product]: ...
