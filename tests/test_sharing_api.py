from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from org.models import Department
from assistants.models import Assistant, AssistantUserAccess, AssistantDepartmentAccess, AssistantPermission

class AssistantSharingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.sales = Department.objects.create(name="Sales")
        self.support = Department.objects.create(name="Support")
        self.owner = User.objects.create_user(username="owner", password="pw", department=self.sales)
        self.other = User.objects.create_user(username="other", password="pw", department=self.support)
        self.third = User.objects.create_user(username="third", password="pw", department=self.support)
        self.asst = Assistant.objects.create(name="Share", owner=self.owner)

    def _auth(self, user):
        resp = self.client.post(
            "/api/token/",
            {"username": user.username, "password": "pw"},
            format="json",
        )
        token = resp.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_owner_can_add_user_share(self):
        self._auth(self.owner)
        resp = self.client.post(
            f"/api/assistants/{self.asst.id}/shares/users/",
            {"user": self.other.id, "permission": "use"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(
            AssistantUserAccess.objects.filter(
                assistant=self.asst, user=self.other, permission=AssistantPermission.USE
            ).exists()
        )

    def test_repost_updates_permission(self):
        AssistantUserAccess.objects.create(
            assistant=self.asst, user=self.other, permission=AssistantPermission.USE
        )
        self._auth(self.owner)
        resp = self.client.post(
            f"/api/assistants/{self.asst.id}/shares/users/",
            {"user": self.other.id, "permission": "edit"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        access = AssistantUserAccess.objects.get(assistant=self.asst, user=self.other)
        self.assertEqual(access.permission, AssistantPermission.EDIT)

    def test_non_owner_forbidden(self):
        self._auth(self.other)
        resp = self.client.post(
            f"/api/assistants/{self.asst.id}/shares/users/",
            {"user": self.third.id, "permission": "use"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_owner_can_remove_user(self):
        AssistantUserAccess.objects.create(
            assistant=self.asst, user=self.other, permission=AssistantPermission.USE
        )
        self._auth(self.owner)
        resp = self.client.delete(
            f"/api/assistants/{self.asst.id}/shares/users/{self.other.id}/"
        )
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(
            AssistantUserAccess.objects.filter(assistant=self.asst, user=self.other).exists()
        )
        self._auth(self.other)
        resp = self.client.get("/api/assistants/")
        self.assertEqual(resp.json(), [])

    def test_department_share_applies_to_new_user(self):
        self._auth(self.owner)
        resp = self.client.post(
            f"/api/assistants/{self.asst.id}/shares/departments/",
            {"department": self.support.id, "permission": "use"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        new_user = get_user_model().objects.create_user(
            username="new", password="pw", department=self.support
        )
        self._auth(new_user)
        resp = self.client.get("/api/assistants/")
        ids = [a["id"] for a in resp.json()]
        self.assertIn(str(self.asst.id), ids)

    def test_owner_cannot_remove_self(self):
        self._auth(self.owner)
        resp = self.client.delete(
            f"/api/assistants/{self.asst.id}/shares/users/{self.owner.id}/"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Owner", resp.json().get("detail", ""))

