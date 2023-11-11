from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class HwkUser(AbstractUser):
    """Custom user"""
    approved = models.BooleanField(default=False)

    def __str__(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        return {self.username}


class Holiday(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username}'s holiday from {self.from_time} to {self.to_time}"
