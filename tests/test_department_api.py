from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from org.models import Department


class DepartmentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        self.user = User.objects.create_user(
            username="user", password="pass", is_staff=False
        )

    def _auth(self, user):
        resp = self.client.post(
            "/api/token/",
            {"username": user.username, "password": "pass"},
            format="json",
        )
        token = resp.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_public_list(self):
        Department.objects.create(name="HR")
        resp = self.client.get("/api/departments/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)

    def test_admin_can_create(self):
        self._auth(self.admin)
        resp = self.client.post(
            "/api/departments/",
            {"name": "Research"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Department.objects.filter(name="Research").exists())

    def test_non_admin_cannot_create(self):
        self._auth(self.user)
        resp = self.client.post(
            "/api/departments/",
            {"name": "Blocked"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_duplicate_name(self):
        Department.objects.create(name="Sales")
        self._auth(self.admin)
        resp = self.client.post(
            "/api/departments/",
            {"name": "Sales"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_admin_update_and_delete(self):
        dept = Department.objects.create(name="Ops")
        self._auth(self.admin)
        resp = self.client.patch(
            f"/api/departments/{dept.id}/",
            {"name": "Operations"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Department.objects.filter(name="Operations").exists())
        resp = self.client.delete(f"/api/departments/{dept.id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Department.objects.filter(id=dept.id).exists())
