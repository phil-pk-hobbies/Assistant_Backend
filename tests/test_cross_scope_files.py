from django.test import TestCase
from django.contrib.auth import get_user_model
from org.models import Department
from assistants.models import Assistant, AssistantFile
from chat.models import Thread, ThreadFile
from django.core.exceptions import ValidationError


class CrossScopeFileTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.dept = Department.objects.create(name="Dept")
        self.user = User.objects.create_user(username="u", password="pw", department=self.dept)
        self.asst = Assistant.objects.create(name="A", owner=self.user)
        self.thread = Thread.objects.create(assistant=self.asst, user=self.user)

    def test_assistant_file_blocks_thread_file(self):
        AssistantFile.objects.create(
            assistant=self.asst,
            user=self.user,
            original_name="a.txt",
            file_id="file_dupe",
            size_bytes=1,
        )
        with self.assertRaises(ValidationError):
            ThreadFile.objects.create(
                thread=self.thread,
                user=self.user,
                original_name="b.txt",
                file_id="file_dupe",
                size_bytes=1,
            )

    def test_thread_file_blocks_assistant_file(self):
        ThreadFile.objects.create(
            thread=self.thread,
            user=self.user,
            original_name="t.txt",
            file_id="file_dupe2",
            size_bytes=1,
        )
        with self.assertRaises(ValidationError):
            AssistantFile.objects.create(
                assistant=self.asst,
                user=self.user,
                original_name="a.txt",
                file_id="file_dupe2",
                size_bytes=1,
            )
