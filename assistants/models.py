"""
SQLite-backed models for assistants and their messages.
"""
import uuid
from django.db import models
from django.conf import settings
from .managers import AssistantQuerySet
from file_utils import assert_fileid_unique_across_models
from django.db import transaction

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


class AssistantPermission(models.TextChoices):
    USE = "use", "Use"
    EDIT = "edit", "Edit"


class Assistant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_assistants",
        on_delete=models.CASCADE,
    )
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
    openai_id  = models.CharField(max_length=40, blank=True, null=True)  # asst_...
    thread_id  = models.CharField(max_length=40, blank=True, null=True)  # thr_...
    vector_store_id = models.CharField(max_length=40, blank=True, null=True)

    objects = AssistantQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    def permission_for(self, user):
        if user == self.owner:
            return AssistantPermission.EDIT
        perms = []
        ua = self.user_access.filter(user=user).first()
        if ua:
            perms.append(ua.permission)
        if getattr(user, "department_id", None):
            da = self.dept_access.filter(department_id=user.department_id).first()
            if da:
                perms.append(da.permission)
        if AssistantPermission.EDIT in perms:
            return AssistantPermission.EDIT
        if AssistantPermission.USE in perms:
            return AssistantPermission.USE
        return None


class AssistantUserAccess(models.Model):
    assistant = models.ForeignKey(Assistant, related_name="user_access", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="assistant_access", on_delete=models.CASCADE)
    permission = models.CharField(max_length=4, choices=AssistantPermission.choices)

    class Meta:
        unique_together = ("assistant", "user")


class AssistantDepartmentAccess(models.Model):
    assistant = models.ForeignKey(Assistant, related_name="dept_access", on_delete=models.CASCADE)
    department = models.ForeignKey('org.Department', related_name="assistant_access", on_delete=models.CASCADE)
    permission = models.CharField(max_length=4, choices=AssistantPermission.choices)

    class Meta:
        unique_together = ("assistant", "department")


class Message(models.Model):
    ROLE_CHOICES = [('system', 'system'), ('user', 'user'), ('assistant', 'assistant')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class AssistantFile(models.Model):
    STATUS_CHOICES = [
        ("uploading", "Uploading"),
        ("ready", "Ready"),
        ("error", "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        Assistant, on_delete=models.CASCADE, related_name="files"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assistant_files"
    )
    original_name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=64, unique=True)
    size_bytes = models.BigIntegerField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="uploading")
    error_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"assistant-{self.assistant_id}: {self.original_name}"

    def clean(self):
        assert_fileid_unique_across_models(self.file_id)
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            assert_fileid_unique_across_models(self.file_id, lock=True)
            return super().save(*args, **kwargs)
