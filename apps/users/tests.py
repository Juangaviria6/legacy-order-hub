from rest_framework.test import APITestCase
from django.test import TestCase

from apps.users.infrastructure.repositories import DjangoUserRepository
from apps.users.models import UserModel


class LoginViewTests(APITestCase):
    def setUp(self):
        UserModel.objects.create_user(
            username="testuser", password="123456", role="client"
        )

    def test_login_with_valid_credentials_returns_user_and_tokens(self):
        response = self.client.post(
            "/login", {"username": "testuser", "password": "123456"}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["user"]["username"], "testuser")
        self.assertEqual(body["user"]["role"], "client")
        self.assertTrue(body["access"])
        self.assertTrue(body["refresh"])

    def test_login_with_invalid_credentials_returns_401(self):
        response = self.client.post(
            "/login", {"username": "testuser", "password": "wrong"}, format="json"
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["status"], "error")

    def test_login_with_nonexistent_username_returns_401(self):
        response = self.client.post(
            "/login", {"username": "ghost", "password": "whatever"}, format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_login_without_credentials_returns_400(self):
        response = self.client.post("/login", {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "error")

    def test_token_refresh_with_valid_refresh_token_returns_new_access(self):
        login_response = self.client.post(
            "/login", {"username": "testuser", "password": "123456"}, format="json"
        )
        refresh_token = login_response.json()["refresh"]

        response = self.client.post(
            "/token/refresh", {"refresh": refresh_token}, format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["access"])

    def test_token_refresh_with_invalid_token_returns_401(self):
        response = self.client.post(
            "/token/refresh", {"refresh": "not-a-valid-token"}, format="json"
        )

        self.assertEqual(response.status_code, 401)


class SeedDataHashingTests(TestCase):
    def test_seeded_admin_password_is_hashed_with_argon2(self):
        admin = UserModel.objects.get(username="admin")

        self.assertTrue(admin.password.startswith("argon2$"))
        self.assertNotEqual(admin.password, "admin123")
        self.assertTrue(admin.check_password("admin123"))
        self.assertEqual(admin.role, "admin")


class DjangoUserRepositoryTests(TestCase):
    def setUp(self):
        self.repository = DjangoUserRepository()
        UserModel.objects.create_user(
            username="testuser", password="123456", role="client"
        )

    def test_get_by_credentials_with_correct_password_returns_user(self):
        user = self.repository.get_by_credentials("testuser", "123456")

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "client")

    def test_get_by_credentials_with_wrong_password_returns_none(self):
        self.assertIsNone(self.repository.get_by_credentials("testuser", "wrong"))

    def test_get_by_credentials_with_unknown_username_returns_none(self):
        self.assertIsNone(self.repository.get_by_credentials("ghost", "123456"))
