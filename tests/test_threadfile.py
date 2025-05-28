from django.test import TestCase
from django.contrib.auth import get_user_model
from org.models import Department
from assistants.models import Assistant
from chat.models import Thread, ThreadFile
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class ThreadFileTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.dept = Department.objects.create(name="Dept")
        self.user = User.objects.create_user(username="u", password="pw", department=self.dept)
        self.asst = Assistant.objects.create(name="A", owner=self.user)
        self.thread = Thread.objects.create(assistant=self.asst, user=self.user)

    def test_factory_creates_valid(self):
        tf = ThreadFile.objects.create(
            thread=self.thread,
            user=self.user,
            original_name="f.txt",
            file_id="file_123",
            size_bytes=10,
            mime_type="text/plain",
        )
        self.assertEqual(tf.status, "uploading")
        self.assertIsNotNone(tf.created_at)

    def test_unique_constraint(self):
        ThreadFile.objects.create(
            thread=self.thread,
            user=self.user,
            original_name="f.txt",
            file_id="file_123",
            size_bytes=10,
        )
        with self.assertRaises(IntegrityError):
            ThreadFile.objects.create(
                thread=self.thread,
                user=self.user,
                original_name="g.txt",
                file_id="file_123",
                size_bytes=20,
            )

    def test_invalid_status(self):
        tf = ThreadFile(
            thread=self.thread,
            user=self.user,
            original_name="f.txt",
            file_id="file_456",
            size_bytes=5,
            status="bad",
        )
        with self.assertRaises(ValidationError):
            tf.full_clean()

    def test_str(self):
        tf = ThreadFile.objects.create(
            thread=self.thread,
            user=self.user,
            original_name="f.txt",
            file_id="file_123",
            size_bytes=1,
        )
        self.assertEqual(str(tf), f"thread-{self.thread.id}: f.txt")

    def test_timestamps_update(self):
        tf = ThreadFile.objects.create(
            thread=self.thread,
            user=self.user,
            original_name="f.txt",
            file_id="file_123",
            size_bytes=1,
        )
        orig_created = tf.created_at
        tf.status = "ready"
        tf.save()
        self.assertNotEqual(tf.updated_at, orig_created)
