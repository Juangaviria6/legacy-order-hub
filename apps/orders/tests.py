from unittest.mock import MagicMock, patch

import redis
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APITestCase

from apps.catalog.models import ProductModel
from apps.orders.api.views import _build_notifier
from apps.orders.domain.entities import Order
from apps.orders.infrastructure.notifier import (
    CompositeNotifier,
    RedisStreamNotifier,
    ThreadedLogNotifier,
)
from apps.users.models import UserModel


@override_settings(REDIS_URL="")
class OrdersApiTests(APITestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="testuser", password="123456"
        )
        self.other = UserModel.objects.create_user(username="other", password="123456")
        self.admin = UserModel.objects.create_user(
            username="boss", password="123456", role="admin"
        )
        self.product = ProductModel.objects.create(
            name="Mouse USB", price=15.50, stock=5
        )
        self.client.force_authenticate(self.user)

    def _order(self, **payload):
        payload.setdefault("product_id", self.product.id)
        return self.client.post("/create_order", payload, format="json")

    def test_create_order_success_uses_authenticated_user(self):
        response = self._order(quantity=2)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["total"], 31.0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        orders = self.client.get("/get_all_orders_legacy").json()
        self.assertEqual(orders[0]["user_id"], self.user.id)

    def test_create_order_ignores_user_id_in_body(self):
        self._order(quantity=1, user_id=self.other.id)

        orders = self.client.get("/get_all_orders_legacy").json()
        self.assertEqual(orders[0]["user_id"], self.user.id)

    def test_create_order_requires_authentication(self):
        self.client.force_authenticate(None)

        self.assertEqual(self._order(quantity=1).status_code, 401)

    def test_create_order_insufficient_stock_returns_400(self):
        self.assertEqual(self._order(quantity=100).status_code, 400)

    def test_create_order_product_not_found_returns_404(self):
        self.assertEqual(self._order(product_id=9999).status_code, 404)

    def test_create_order_invalid_quantity_returns_400(self):
        for quantity in (0, -3, "abc"):
            with self.subTest(quantity=quantity):
                self.assertEqual(self._order(quantity=quantity).status_code, 400)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_create_order_missing_product_returns_400(self):
        response = self.client.post("/create_order", {"quantity": 1}, format="json")

        self.assertEqual(response.status_code, 400)

    def test_list_orders_requires_authentication(self):
        self.client.force_authenticate(None)

        self.assertEqual(self.client.get("/get_all_orders_legacy").status_code, 401)

    def test_client_only_sees_own_orders(self):
        self._order(quantity=1)
        self.client.force_authenticate(self.other)
        self._order(quantity=1)

        body = self.client.get("/get_all_orders_legacy").json()

        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["user_id"], self.other.id)

    def test_admin_sees_all_orders(self):
        self._order(quantity=1)
        self.client.force_authenticate(self.other)
        self._order(quantity=1)
        self.client.force_authenticate(self.admin)

        body = self.client.get("/get_all_orders_legacy").json()

        self.assertEqual(len(body), 2)

    @patch("apps.orders.infrastructure.notifier.ThreadedLogNotifier._executor")
    def test_notification_is_sent_after_commit_without_blocking(self, executor):
        with self.captureOnCommitCallbacks(execute=True) as callbacks:
            response = self._order(quantity=1)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(callbacks), 1)
        executor.submit.assert_called_once()

    @patch("apps.orders.infrastructure.notifier.ThreadedLogNotifier._executor")
    def test_no_notification_when_order_is_rejected(self, executor):
        with self.captureOnCommitCallbacks(execute=True):
            self._order(quantity=100)

        executor.submit.assert_not_called()


class RedisNotifierTests(SimpleTestCase):
    ORDER = Order(id=1, user_id=2, product_id=3, quantity=1, total=9.5)

    @patch("apps.orders.infrastructure.notifier.redis.Redis.from_url")
    def test_publish_adds_event_to_stream(self, from_url):
        notifier = RedisStreamNotifier("redis://localhost:6379/0")

        notifier._publish(self.ORDER)

        from_url.return_value.xadd.assert_called_once()
        args = from_url.return_value.xadd.call_args
        self.assertEqual(args.args[0], RedisStreamNotifier.STREAM)
        self.assertEqual(args.args[1]["order_id"], 1)

    @patch("apps.orders.infrastructure.notifier.redis.Redis.from_url")
    def test_publish_swallows_redis_errors(self, from_url):
        from_url.return_value.xadd.side_effect = redis.ConnectionError("down")
        notifier = RedisStreamNotifier("redis://localhost:6379/0")

        with self.assertLogs("orderhub.notifications", level="ERROR"):
            notifier._publish(self.ORDER)

    @patch("apps.orders.infrastructure.notifier.redis.Redis.from_url")
    def test_order_created_does_not_block(self, from_url):
        notifier = RedisStreamNotifier("redis://localhost:6379/0")
        with patch.object(RedisStreamNotifier, "_executor") as executor:
            notifier.order_created(self.ORDER)

        executor.submit.assert_called_once()

    def test_composite_notifies_all(self):
        first, second = MagicMock(), MagicMock()

        CompositeNotifier(first, second).order_created(self.ORDER)

        first.order_created.assert_called_once_with(self.ORDER)
        second.order_created.assert_called_once_with(self.ORDER)

    @override_settings(REDIS_URL="")
    def test_builder_without_redis_uses_log_notifier_only(self):
        self.assertIsInstance(_build_notifier(), ThreadedLogNotifier)

    @override_settings(REDIS_URL="redis://localhost:6379/0")
    @patch("apps.orders.infrastructure.notifier.redis.Redis.from_url")
    def test_builder_with_redis_uses_composite(self, from_url):
        self.assertIsInstance(_build_notifier(), CompositeNotifier)
