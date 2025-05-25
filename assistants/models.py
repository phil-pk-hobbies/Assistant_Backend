"""
SQLite-backed models for assistants and their messages.
"""
import uuid
from django.db import models


class Assistant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    instructions = models.TextField(blank=True)
    tools = models.JSONField(default=list, help_text="e.g. ['code_interpreter']")
    created_at = models.DateTimeField(auto_now_add=True)
    openai_id  = models.CharField(max_length=40, blank=True, null=True)  # asst_…
    thread_id  = models.CharField(max_length=40, blank=True, null=True)  # thr_…

    def __str__(self) -> str:
        return self.name


class Message(models.Model):
    ROLE_CHOICES = [('system', 'system'), ('user', 'user'), ('assistant', 'assistant')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
