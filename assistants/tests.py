from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from .models import Assistant, Message


class ChatHistoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.asst = Assistant.objects.create(name="tester")
        Message.objects.create(assistant=self.asst, role="user", content="hi")
        Message.objects.create(assistant=self.asst, role="assistant", content="hello")

    def test_history_endpoint_returns_messages(self):
        url = reverse('chat-history', args=[self.asst.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

