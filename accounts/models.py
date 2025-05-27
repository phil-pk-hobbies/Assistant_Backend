from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    department = models.ForeignKey(
        'org.Department',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
