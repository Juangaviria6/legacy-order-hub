from apps.catalog.domain.entities import Product
from apps.catalog.domain.ports import ProductRepositoryPort
from apps.catalog.models import ProductModel


class DjangoProductRepository(ProductRepositoryPort):
    def get_by_id(self, product_id: int) -> Product | None:
        row = ProductModel.objects.filter(id=product_id).first()
        if row is None:
            return None
        return Product(id=row.id, name=row.name, price=row.price, stock=row.stock)

    def get_by_id_for_update(self, product_id: int) -> Product | None:
        row = ProductModel.objects.select_for_update().filter(id=product_id).first()
        if row is None:
            return None
        return Product(id=row.id, name=row.name, price=row.price, stock=row.stock)

    def create(self, name: str, price: float, stock: int) -> int:
        row = ProductModel.objects.create(name=name, price=price, stock=stock)
        return row.id

    def update_stock(self, product_id: int, new_stock: int) -> None:
        ProductModel.objects.filter(id=product_id).update(stock=new_stock)

    def list_all(self) -> list[Product]:
        return [
            Product(id=row.id, name=row.name, price=row.price, stock=row.stock)
            for row in ProductModel.objects.all()
        ]
