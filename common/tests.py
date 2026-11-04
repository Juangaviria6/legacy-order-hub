import json
import logging
from types import SimpleNamespace

from django.test import TestCase

from common.api.permissions import IsAdminRole
from common.observability.logging import JsonFormatter


class IsAdminRoleTests(TestCase):
    def setUp(self):
        self.permission = IsAdminRole()

    def _request_with_user(self, is_authenticated, role=None):
        user = SimpleNamespace(is_authenticated=is_authenticated, role=role)
        return SimpleNamespace(user=user)

    def test_admin_role_is_allowed(self):
        request = self._request_with_user(is_authenticated=True, role="admin")

        self.assertTrue(self.permission.has_permission(request, None))

    def test_client_role_is_denied(self):
        request = self._request_with_user(is_authenticated=True, role="client")

        self.assertFalse(self.permission.has_permission(request, None))

    def test_unauthenticated_user_is_denied(self):
        request = self._request_with_user(is_authenticated=False, role="admin")

        self.assertFalse(self.permission.has_permission(request, None))


class ObservabilityTests(TestCase):
    def test_healthcheck_reports_ok(self):
        response = self.client.get("/healthcheck")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_metrics_endpoint_exposes_prometheus_format(self):
        self.client.get("/healthcheck")

        response = self.client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertIn("django_http_requests_total_by_method", response.content.decode())
        self.assertIn("orderhub_orders_created_total", response.content.decode())

    def test_json_formatter_includes_timestamp_level_and_context(self):
        record = logging.LogRecord(
            "x", logging.INFO, "f", 1, "hola %s", ("mundo",), None
        )
        record.order_id = 7

        data = json.loads(JsonFormatter().format(record))

        self.assertEqual(data["message"], "hola mundo")
        self.assertEqual(data["level"], "INFO")
        self.assertEqual(data["order_id"], 7)
        self.assertIn("timestamp", data)
