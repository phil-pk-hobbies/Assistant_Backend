"""
SQLite-backed models for assistants and their messages.
"""
import uuid
from django.db import models

# ─────────────────────────────────────────────────────────────────────────────
#  Allowed assistant models
# ─────────────────────────────────────────────────────────────────────────────
ALLOWED_MODELS = ["gpt-4", "gpt-4o", "o1-mini", "o3-mini", "o:mini"]

# Supported reasoning effort levels
REASONING_EFFORT_CHOICES = [
    ("low", "low"),
    ("medium", "medium"),
    ("high", "high"),
]


class Assistant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True)
    tools = models.JSONField(default=list, help_text="e.g. ['code_interpreter']")
    MODEL_CHOICES = [(m, m) for m in ALLOWED_MODELS]
    model = models.CharField(max_length=40, default="gpt-4o", choices=MODEL_CHOICES)
    reasoning_effort = models.CharField(
        max_length=6,
        choices=REASONING_EFFORT_CHOICES,
        default="medium",
    )
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
