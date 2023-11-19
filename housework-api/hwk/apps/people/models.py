from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


def preferences_factory():
    return {"version": "1"}


class HwkUser(AbstractUser):
    """Custom user"""
    first_name = None
    last_name = None
    short_name = models.CharField(max_length=64, null=True, blank=True)
    full_name = models.CharField(max_length=256, null=True, blank=True)
    approved = models.BooleanField(default=False)
    preferences = models.JSONField(default=preferences_factory)

    def __str__(self):
        if self.full_name:
            return f"{self.full_name}"
        return self.username

    def is_set_up(self):
        if self.short_name is None or self.short_name == '':
            return False

        if self.full_name is None or self.full_name == '':
            return False

        if self.email is None or self.email == '':
            return False

        if not self.has_usable_password():
            return False

        return True


class Holiday(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}'s holiday from {self.from_time} to {self.to_time}"
