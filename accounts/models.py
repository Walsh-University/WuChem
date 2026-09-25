from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        FACULTY = "faculty", "Faculty"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=32, choices=Role, default=Role.STUDENT)

    @property
    def display_name(self):
        return self.get_full_name() or self.get_username()

    @property
    def can_manage_inventory(self):
        return self.is_superuser or self.role in {self.Role.FACULTY, self.Role.ADMIN}

    @property
    def can_manage_system(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        self.is_staff = self.is_superuser or self.role == self.Role.ADMIN
        super().save(*args, **kwargs)
