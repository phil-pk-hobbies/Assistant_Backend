from rest_framework.permissions import BasePermission


class AssistantPermission(BasePermission):
    """Object-level permission checks for assistants."""

    def has_object_permission(self, request, view, obj):
        perm = obj.permission_for(request.user)
        if view.action in ("retrieve", "execute"):
            return perm in ("use", "edit") or obj.owner == request.user
        if view.action in ("update", "partial_update", "destroy"):
            return perm == "edit" or obj.owner == request.user
        return False
