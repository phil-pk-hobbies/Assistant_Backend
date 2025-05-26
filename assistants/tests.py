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


class CreateAssistantModelTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_assistant_stores_model(self):
        create_mock = MagicMock(return_value=types.SimpleNamespace(id="asst_999"))

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(create=create_mock))
                self.files = types.SimpleNamespace(create=MagicMock())

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.post('/api/assistants/', {
                'name': 'Test',
                'model': 'gpt-3.5-turbo',
            }, format='json')

        self.assertEqual(resp.status_code, 201)
        asst = Assistant.objects.get(name='Test')
        self.assertEqual(asst.model, 'gpt-3.5-turbo')


class UpdateAssistantTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_update_assistant_updates_remote(self):
        assistant = Assistant.objects.create(
            name='Orig', instructions='inst', description='desc',
            tools=['code_interpreter'], openai_id='asst_987'
        )

        update_mock = MagicMock()

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(update=update_mock))

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.patch(
                f'/api/assistants/{assistant.id}/',
                {'name': 'New', 'description': 'new desc'},
                format='json'
            )

        self.assertEqual(resp.status_code, 200)
        assistant.refresh_from_db()
        self.assertEqual(assistant.name, 'New')
        update_mock.assert_called_with(
            assistant.openai_id,
            name='New',
            description='new desc',
            instructions='inst',
            model=assistant.model,
            tools=[{'type': 'code_interpreter'}]
        )

