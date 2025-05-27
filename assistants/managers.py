from django.db import models
from django.db.models import Q


class AssistantQuerySet(models.QuerySet):
    def for_user(self, user):
        q = Q(owner=user) | Q(user_access__user=user)
        if getattr(user, "department_id", None):
            q |= Q(dept_access__department_id=user.department_id)
        return self.filter(q).distinct()

