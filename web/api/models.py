import secrets

from django.db import models


def generate_token():
    return secrets.token_hex(20)


class ApiClient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    token = models.CharField(max_length=40, unique=True, default=generate_token)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
