from django.test import TestCase
from rest_framework.test import APIClient
from .models import Assistant
from unittest.mock import MagicMock, patch
import types
import sys

class DeleteAssistantTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_delete_assistant_removes_remote(self):
        # create a dummy assistant
        assistant = Assistant.objects.create(name="Test", openai_id="asst_123")

        delete_mock = MagicMock()

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(delete=delete_mock))

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.delete(f'/api/assistants/{assistant.id}/')

        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Assistant.objects.filter(id=assistant.id).exists())
        delete_mock.assert_called_with(assistant.openai_id)

