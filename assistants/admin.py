from django.contrib import admin
from .models import Assistant, Message


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    readonly_fields = ("openai_id", "thread_id", "created_at")
    fields = ("name", "description", "instructions", "tools", "openai_id", "thread_id", "created_at")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("assistant", "role", "created_at")
    readonly_fields = ("created_at",)
