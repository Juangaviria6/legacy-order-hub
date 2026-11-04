from dataclasses import dataclass


@dataclass
class Order:
    id: int | None = None
    user_id: int | None = None
    product_id: int | None = None
    quantity: int = 0
    total: float = 0.0
    status: str = "PENDING"
