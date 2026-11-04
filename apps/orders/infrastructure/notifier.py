import logging
from concurrent.futures import ThreadPoolExecutor

import redis

from apps.orders.domain.entities import Order
from apps.orders.domain.ports import NotificationPort

logger = logging.getLogger("orderhub.notifications")


class ThreadedLogNotifier(NotificationPort):
    """Notifica en un hilo aparte para no bloquear la respuesta HTTP."""

    _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="notifier")

    def order_created(self, order: Order) -> None:
        self._executor.submit(self._send, order)

    @staticmethod
    def _send(order: Order) -> None:
        logger.info(
            "Notificación de orden creada",
            extra={
                "event": "order_created",
                "order_id": order.id,
                "user_id": order.user_id,
                "total": order.total,
            },
        )


class RedisStreamNotifier(NotificationPort):
    """Publica el evento en un stream de Redis, fuera del hilo de la petición."""

    STREAM = "orderhub:order_created"
    _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="redis-notifier")

    def __init__(self, redis_url: str):
        self._client = redis.Redis.from_url(redis_url, socket_timeout=2)

    def order_created(self, order: Order) -> None:
        self._executor.submit(self._publish, order)

    def _publish(self, order: Order) -> None:
        try:
            self._client.xadd(
                self.STREAM,
                {
                    "order_id": order.id,
                    "user_id": order.user_id,
                    "total": order.total,
                },
                maxlen=10000,
                approximate=True,
            )
        except redis.RedisError:
            logger.exception(
                "No se pudo publicar el evento en Redis",
                extra={"event": "redis_publish_failed", "order_id": order.id},
            )


class CompositeNotifier(NotificationPort):
    def __init__(self, *notifiers: NotificationPort):
        self._notifiers = notifiers

    def order_created(self, order: Order) -> None:
        for notifier in self._notifiers:
            notifier.order_created(order)
