from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Assistant, Message
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
                'model': 'gpt-4',
            }, format='json')

        self.assertEqual(resp.status_code, 201)
        asst = Assistant.objects.get(name='Test')
        self.assertEqual(asst.model, 'gpt-4')

    def test_create_with_file_search_tool(self):
        create_mock = MagicMock(return_value=types.SimpleNamespace(id="asst_fs"))

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(create=create_mock))
                self.files = types.SimpleNamespace(create=MagicMock())

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.post('/api/assistants/', {
                'name': 'FS',
                'model': 'gpt-4o',
                'tools': ['file_search'],
            }, format='json')

        self.assertEqual(resp.status_code, 201)
        create_mock.assert_called()

    def test_file_search_with_files_creates_vector_store(self):
        create_mock = MagicMock(return_value=types.SimpleNamespace(id="asst_up"))
        file_create_mock = MagicMock(return_value=types.SimpleNamespace(id="file_1"))
        vector_store_mock = MagicMock(return_value=types.SimpleNamespace(id="vs_1"))

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(
                    assistants=types.SimpleNamespace(create=create_mock),
                    vector_stores=types.SimpleNamespace(create=vector_store_mock),
                )
                self.files = types.SimpleNamespace(create=file_create_mock)

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        file_obj = SimpleUploadedFile("foo.txt", b"data", content_type="text/plain")

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.post(
                '/api/assistants/',
                {
                    'name': 'FSF',
                    'model': 'gpt-4o',
                    'tools': ['file_search'],
                    'files': [file_obj],
                },
                format='multipart'
            )

        self.assertEqual(resp.status_code, 201)
        vector_store_mock.assert_called()

    def test_create_with_invalid_tool_fails(self):
        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(create=MagicMock()))
                self.files = types.SimpleNamespace(create=MagicMock())

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.post('/api/assistants/', {
                'name': 'Bad',
                'model': 'gpt-4o',
                'tools': ['code_interpreter'],
            }, format='json')

        self.assertEqual(resp.status_code, 400)

    def test_create_assistant_invalid_model_fails(self):
        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(create=MagicMock()))
                self.files = types.SimpleNamespace(create=MagicMock())

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.post('/api/assistants/', {
                'name': 'TestBad',
                'model': 'gpt-3.5-turbo',
            }, format='json')

        self.assertEqual(resp.status_code, 400)


class UpdateAssistantTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_update_assistant_updates_remote(self):
        assistant = Assistant.objects.create(
            name='Orig', instructions='inst', description='desc',
            tools=['file_search'], openai_id='asst_987'
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
            tools=[{'type': 'file_search'}]
        )


class UpdateAssistantNoToolsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_update_assistant_without_tools(self):
        assistant = Assistant.objects.create(
            name='Orig', instructions='', description='',
            tools=[], openai_id='asst_empty'
        )

        update_mock = MagicMock()

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(assistants=types.SimpleNamespace(update=update_mock))

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.patch(
                f'/api/assistants/{assistant.id}/',
                {'name': 'NewName'},
                format='json'
            )

        self.assertEqual(resp.status_code, 200)
        update_mock.assert_called_with(
            assistant.openai_id,
            name='NewName',
            description='',
            instructions='',
            model=assistant.model,
            tools=[]
        )


class ResetThreadTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_reset_thread_deletes_remote_and_messages(self):
        assistant = Assistant.objects.create(name='Test', thread_id='thr_123')
        Message.objects.create(assistant=assistant, role='user', content='hi')

        delete_mock = MagicMock()

        class DummyClient:
            def __init__(self):
                self.beta = types.SimpleNamespace(threads=types.SimpleNamespace(delete=delete_mock))

        dummy_openai = types.SimpleNamespace(OpenAI=lambda api_key=None: DummyClient())

        with patch.dict(sys.modules, {'openai': dummy_openai}):
            resp = self.client.post(f'/api/assistants/{assistant.id}/reset/')

        self.assertEqual(resp.status_code, 204)
        assistant.refresh_from_db()
        self.assertIsNone(assistant.thread_id)
        self.assertFalse(Message.objects.filter(assistant=assistant).exists())
        delete_mock.assert_called_with('thr_123')


