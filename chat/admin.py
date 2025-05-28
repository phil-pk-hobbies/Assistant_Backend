from django.contrib import admin
from .models import ThreadFile

@admin.register(ThreadFile)
class ThreadFileAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "original_name", "status", "size_bytes", "created_at")
    list_filter = ("status", "created_at")
