from prometheus_client import Counter

ORDERS_CREATED = Counter(
    "orderhub_orders_created_total", "Número de órdenes procesadas con éxito"
)
