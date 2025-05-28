import uuid
from django.db import models, transaction
from django.conf import settings
from file_utils import assert_fileid_unique_across_models

class Thread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey('assistants.Assistant', on_delete=models.CASCADE, related_name='threads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='threads')
    openai_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assistant', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.assistant.name} / {self.user.username}" if self.assistant_id and self.user_id else str(self.id)

class ThreadFile(models.Model):
    STATUS_CHOICES = [
        ("uploading", "Uploading"),
        ("ready", "Ready"),
        ("error", "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='files')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='thread_files')
    original_name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=64, unique=True)
    size_bytes = models.BigIntegerField()
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='uploading')
    error_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('thread', 'file_id')
        indexes = [
            models.Index(fields=['thread', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"thread-{self.thread_id}: {self.original_name}"

    def clean(self):
        assert_fileid_unique_across_models(self.file_id)
        return super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        with transaction.atomic():
            assert_fileid_unique_across_models(self.file_id, lock=True)
            return super().save(*args, **kwargs)
