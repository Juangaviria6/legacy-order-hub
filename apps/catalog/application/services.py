from apps.catalog.domain.ports import ProductRepositoryPort


class CatalogService:
    def __init__(self, product_repository: ProductRepositoryPort):
        self._product_repository = product_repository

    def create_product(self, name: str, price, stock) -> int:
        if not name or price is None or stock is None:
            raise ValueError("Faltan datos para crear el producto")

        return self._product_repository.create(name, float(price), int(stock))

    def list_products(self):
        return self._product_repository.list_all()
