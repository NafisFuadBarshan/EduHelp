from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Students and teachers sign up themselves; admins are staff users."""

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT and not self.is_staff
