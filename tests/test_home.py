from django.test import TestCase


class DashboardViewTests(TestCase):
    def test_index_renders(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_index_exposes_order_and_product_actions(self):
        html = self.client.get("/").content.decode()

        for action in ("login()", "createOrder()", "createProduct()", "loadOrders()"):
            self.assertIn(action, html)
