from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from org.models import Department
from assistants.models import Assistant, AssistantUserAccess, AssistantPermission
from unittest.mock import MagicMock, patch
import types
import sys


class AssistantAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.dept = Department.objects.create(name="Dept")
        self.owner1 = User.objects.create_user(username="owner1", password="pw", department=self.dept)
        self.owner2 = User.objects.create_user(username="owner2", password="pw", department=self.dept)
        self.use_user = User.objects.create_user(username="use", password="pw", department=self.dept)
        self.edit_user = User.objects.create_user(username="edit", password="pw", department=self.dept)
        self.other = User.objects.create_user(username="other", password="pw", department=self.dept)

        self.asst1 = Assistant.objects.create(name="A1", owner=self.owner1)
        self.asst2 = Assistant.objects.create(name="A2", owner=self.owner2)
        AssistantUserAccess.objects.create(
            assistant=self.asst2,
            user=self.use_user,
            permission=AssistantPermission.USE,
        )
        AssistantUserAccess.objects.create(
            assistant=self.asst2,
            user=self.edit_user,
            permission=AssistantPermission.EDIT,
        )

    def _auth(self, user):
        resp = self.client.post(
            "/api/token/",
            {"username": user.username, "password": "pw"},
            format="json",
        )
        token = resp.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_list_filtered(self):
        self._auth(self.owner1)
        resp = self.client.get("/api/assistants/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["id"], str(self.asst1.id))

        self._auth(self.use_user)
        resp = self.client.get("/api/assistants/")
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["id"], str(self.asst2.id))

        self._auth(self.other)
        resp = self.client.get("/api/assistants/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_retrieve_denied_without_access(self):
        self._auth(self.other)
        resp = self.client.get(f"/api/assistants/{self.asst1.id}/")
        self.assertEqual(resp.status_code, 404)

    def test_update_denied_with_use_only(self):
        self._auth(self.use_user)
        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: MagicMock())
        with patch.dict(sys.modules, {"openai": dummy_openai}):
            resp = self.client.patch(
                f"/api/assistants/{self.asst2.id}/",
                {"name": "X"},
                format="json",
            )
        self.assertEqual(resp.status_code, 403)

    def test_update_allowed_for_edit(self):
        self._auth(self.edit_user)
        update_mock = MagicMock()

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(update=update_mock))

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())
        with patch.dict(sys.modules, {"openai": dummy_openai}):
            resp = self.client.patch(
                f"/api/assistants/{self.asst2.id}/",
                {"name": "New"},
                format="json",
            )
        self.assertEqual(resp.status_code, 200)
        self.asst2.refresh_from_db()
        self.assertEqual(self.asst2.name, "New")

    def test_execute_allowed_for_use(self):
        self._auth(self.use_user)
        message = types.SimpleNamespace(content=[types.SimpleNamespace(text=types.SimpleNamespace(value="hi"))])

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(
                    threads=types.SimpleNamespace(
                        create=lambda: types.SimpleNamespace(id="t1"),
                        messages=types.SimpleNamespace(create=lambda **kwargs: None, list=lambda **kwargs: types.SimpleNamespace(data=[message])),
                        runs=types.SimpleNamespace(create=lambda **kwargs: types.SimpleNamespace(id="r1", status="completed"), retrieve=lambda **kwargs: types.SimpleNamespace(id="r1", status="completed")),
                    )
                )
        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())
        with patch.dict(sys.modules, {"openai": dummy_openai}):
            resp = self.client.post(
                f"/api/assistants/{self.asst2.id}/chat/",
                {"content": "hi"},
                format="json",
            )
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_blocked(self):
        resp = self.client.get("/api/assistants/")
        self.assertEqual(resp.status_code, 401)
