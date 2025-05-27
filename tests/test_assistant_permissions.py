from django.test import TestCase
from django.contrib.auth import get_user_model
from org.models import Department
from assistants.models import (
    Assistant,
    AssistantUserAccess,
    AssistantDepartmentAccess,
    AssistantPermission,
)


class AssistantPermissionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.dept1 = Department.objects.create(name="Dept1")
        self.dept2 = Department.objects.create(name="Dept2")
        self.owner = User.objects.create_user(username="owner", password="pw", department=self.dept1)
        self.user = User.objects.create_user(username="user", password="pw", department=self.dept1)
        self.other = User.objects.create_user(username="other", password="pw", department=self.dept2)

    def test_owner_has_edit(self):
        asst = Assistant.objects.create(name="A", owner=self.owner)
        self.assertEqual(asst.permission_for(self.owner), AssistantPermission.EDIT)

    def test_user_access_use(self):
        asst = Assistant.objects.create(name="A", owner=self.owner)
        AssistantUserAccess.objects.create(assistant=asst, user=self.user, permission=AssistantPermission.USE)
        self.assertEqual(asst.permission_for(self.user), AssistantPermission.USE)

    def test_department_edit_applies(self):
        asst = Assistant.objects.create(name="A", owner=self.owner)
        AssistantDepartmentAccess.objects.create(assistant=asst, department=self.dept2, permission=AssistantPermission.EDIT)
        self.assertEqual(asst.permission_for(self.other), AssistantPermission.EDIT)

    def test_queryset_for_user(self):
        owned = Assistant.objects.create(name="Owned", owner=self.owner)
        user_shared = Assistant.objects.create(name="U", owner=self.owner)
        dept_shared = Assistant.objects.create(name="D", owner=self.owner)
        AssistantUserAccess.objects.create(assistant=user_shared, user=self.user, permission=AssistantPermission.USE)
        AssistantDepartmentAccess.objects.create(assistant=dept_shared, department=self.dept2, permission=AssistantPermission.USE)

        qs_owner = list(Assistant.objects.for_user(self.owner))
        qs_user = list(Assistant.objects.for_user(self.user))
        qs_other = list(Assistant.objects.for_user(self.other))
        self.assertEqual(set(qs_owner), {owned, user_shared, dept_shared})
        self.assertEqual(qs_user, [user_shared])
        self.assertEqual(qs_other, [dept_shared])

    def test_unique_constraint(self):
        asst = Assistant.objects.create(name="A", owner=self.owner)
        AssistantUserAccess.objects.create(assistant=asst, user=self.user, permission=AssistantPermission.USE)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            AssistantUserAccess.objects.create(assistant=asst, user=self.user, permission=AssistantPermission.EDIT)

