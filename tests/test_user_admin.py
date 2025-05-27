from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from org.models import Department


class UserAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.dept = Department.objects.create(name="Sales")
        self.admin = User.objects.create_user(
            username="admin", password="pass", is_staff=True
        )
        self.user = User.objects.create_user(
            username="user", password="pass", is_staff=False, department=self.dept
        )

    def _auth(self, user):
        resp = self.client.post(
            "/api/token/",
            {"username": user.username, "password": "pass"},
            format="json",
        )
        token = resp.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_admin_can_create_user(self):
        self._auth(self.admin)
        resp = self.client.post(
            "/api/users/",
            {
                "username": "jdoe",
                "initial_password": "Start!234",
                "first_name": "John",
                "last_name": "Doe",
                "department": self.dept.id,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        obtain = self.client.post(
            "/api/token/",
            {"username": "jdoe", "password": "Start!234"},
            format="json",
        )
        self.assertEqual(obtain.status_code, 200)

    def test_duplicate_username(self):
        self._auth(self.admin)
        self.client.post(
            "/api/users/",
            {
                "username": "dup",
                "initial_password": "Start!234",
            },
            format="json",
        )
        resp = self.client.post(
            "/api/users/",
            {
                "username": "dup",
                "initial_password": "Start!234",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_admin_can_edit_and_toggle_active(self):
        self._auth(self.admin)
        user = get_user_model().objects.create_user(
            username="edit", password="pass", department=self.dept
        )
        new_dept = Department.objects.create(name="Marketing")
        resp = self.client.patch(
            f"/api/users/{user.id}/",
            {"first_name": "E", "department": new_dept.id, "is_active": False},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertEqual(user.department, new_dept)

    def test_admin_reset_password(self):
        self._auth(self.admin)
        user = get_user_model().objects.create_user(
            username="reset", password="old"
        )
        resp = self.client.post(
            f"/api/users/{user.id}/reset_password/",
            {"new_password": "New!456"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        fail = self.client.post(
            "/api/token/",
            {"username": "reset", "password": "old"},
            format="json",
        )
        self.assertEqual(fail.status_code, 401)
        ok = self.client.post(
            "/api/token/",
            {"username": "reset", "password": "New!456"},
            format="json",
        )
        self.assertEqual(ok.status_code, 200)

    def test_non_admin_forbidden(self):
        self._auth(self.user)
        resp = self.client.get("/api/users/")
        self.assertEqual(resp.status_code, 403)
        resp = self.client.post(
            "/api/users/",
            {"username": "x", "initial_password": "x"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_department_protect(self):
        self._auth(self.admin)
        # user already linked to self.dept in setUp
        resp = self.client.delete(f"/api/departments/{self.dept.id}/")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Cannot delete", resp.json().get("detail", ""))
