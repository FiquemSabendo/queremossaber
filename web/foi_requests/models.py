from django.db import models
from . import utils


class PublicBody(models.Model):
    name = models.CharField(max_length=255, blank=False)
    esic_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FOIRequest(models.Model):
    protocol = models.CharField(
        max_length=8,
        unique=True,
        default=utils.generate_protocol
    )
    esic_protocol = models.CharField(max_length=255)
    moderation_status = models.NullBooleanField()
    moderation_message = models.TextField(blank=True)
    moderated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.protocol


class Message(models.Model):
    foi_request = models.ForeignKey(FOIRequest, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        PublicBody,
        null=True,
        related_name='messages_sent',
        on_delete=models.PROTECT
    )
    receiver = models.ForeignKey(
        PublicBody,
        null=True,
        related_name='messages_received',
        on_delete=models.PROTECT
    )
    title = models.TextField(blank=True)
    body = models.TextField(blank=False)
    sent_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.foi_request_id:
            foi_request = FOIRequest()
            foi_request.save()
            self.foi_request = foi_request
        return super(Message, self).save(*args, **kwargs)
