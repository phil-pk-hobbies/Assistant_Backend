from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="tester", password="pass123"
        )

    def test_token_obtain_success(self):
        resp = self.client.post(
            "/api/token/",
            {"username": "tester", "password": "pass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertTrue(data["access"])
        self.assertTrue(data["refresh"])

    def test_token_obtain_bad_creds(self):
        resp = self.client.post(
            "/api/token/",
            {"username": "tester", "password": "bad"},
            format="json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_token_refresh(self):
        obtain = self.client.post(
            "/api/token/",
            {"username": "tester", "password": "pass123"},
            format="json",
        )
        refresh = obtain.json()["refresh"]
        resp = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.json())

    def test_user_me_requires_auth(self):
        obtain = self.client.post(
            "/api/token/",
            {"username": "tester", "password": "pass123"},
            format="json",
        )
        token = obtain.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], self.user.id)

        self.client.credentials()  # remove auth
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 401)
