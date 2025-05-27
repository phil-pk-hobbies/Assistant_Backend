from django.contrib import admin
from .models import (
    Assistant,
    Message,
    AssistantUserAccess,
    AssistantDepartmentAccess,
)


class AssistantUserAccessInline(admin.TabularInline):
    model = AssistantUserAccess


class AssistantDepartmentAccessInline(admin.TabularInline):
    model = AssistantDepartmentAccess


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    inlines = [AssistantUserAccessInline, AssistantDepartmentAccessInline]
    list_display = ("id", "name", "owner")
    readonly_fields = ("openai_id", "thread_id", "created_at")
    fields = (
        "name",
        "owner",
        "description",
        "instructions",
        "tools",
        "openai_id",
        "thread_id",
        "created_at",
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("assistant", "role", "created_at")
    readonly_fields = ("created_at",)
