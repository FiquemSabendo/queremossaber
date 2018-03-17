from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
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
    esic_protocol = models.CharField(max_length=255, blank=True)
    moderation_status = models.NullBooleanField()
    moderation_message = models.TextField(blank=True)
    moderated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-moderation_status']

    def __init__(self, *args, **kwargs):
        super(FOIRequest, self).__init__(*args, **kwargs)
        self._original_moderation_status = self.moderation_status
        self._original_protocol = self.protocol

    def save(self, *args, **kwargs):
        if self._original_moderation_status != self.moderation_status:
            self.moderated_at = timezone.now()
        if self._original_protocol != self.protocol:
            raise ValidationError(
                {'protocol': _('Protocol can not be changed.')}
            )
        super(FOIRequest, self).save(*args, **kwargs)

    def __str__(self):
        return self.protocol

    @property
    def public_body(self):
        if self._first_message:
            return self._first_message.receiver

    @property
    def _first_message(self):
        return self.message_set.first()


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

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.foi_request_id:
            foi_request = FOIRequest()
            foi_request.save()
            self.foi_request = foi_request
        return super(Message, self).save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('foirequest_detail', args=[self.foi_request.protocol])
