import os
import enum
import hashlib
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import utils


class Esic(models.Model):
    url = models.URLField(unique=True)
    username = models.CharField(max_length=255, blank=True)
    # NOTE: This `username` will be extracted to its own class later, whenever
    # we have multiple accounts per eSIC. Meanwhile, we'll keep it here for
    # simplicity. This is the username in the eSIC system, for systems that
    # have logins.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url


class PublicBody(models.Model):
    UFS = (
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AM', 'Amazonas'),
        ('AP', 'Amapá'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MG', 'Minas Gerais'),
        ('MS', 'Mato Grosso do Sul'),
        ('MT', 'Mato Grosso'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('PR', 'Paraná'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('RS', 'Rio Grande do Sul'),
        ('SC', 'Santa Catarina'),
        ('SE', 'Sergipe'),
        ('SP', 'São Paulo'),
        ('TO', 'Tocantins'),
    )

    # NOTE: We might add a "parent_public_body" attribute later to deal with
    # cases like Secretaria de Meio-Ambiente de São Paulo, whose parent would
    # be the Prefeitura de São Paulo. If the time comes, We can get a very
    # similar relationship by looking for the PublicBodies that are in the
    # same Esic system. This is a pretty clear relationship.
    esic = models.ForeignKey(Esic, null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, blank=False, unique=True)
    municipality = models.CharField(max_length=255, blank=True)
    uf = models.CharField(max_length=2, choices=UFS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FOIRequest(models.Model):
    class STATUS(enum.Enum):
        delayed = _('Delayed')
        finished = _('Finished')
        waiting_government = _('Waiting for government reply')
        waiting_user = _('Waiting for user reply')

    REPLY_DAYS = 20  # Public body has to answer in X days
    APPEAL_DAYS = 10  # Citizen can appeal in X days

    protocol = models.CharField(
        max_length=8,
        unique=True,
        default=utils.generate_protocol
    )
    esic_protocol = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    can_publish = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __init__(self, *args, **kwargs):
        super(FOIRequest, self).__init__(*args, **kwargs)
        self._original_protocol = self.protocol

    def save(self, *args, **kwargs):
        self.clean()
        return super(FOIRequest, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if self._original_protocol != self.protocol:
            raise ValidationError(
                {'protocol': _('Protocol can not be changed.')}
            )
        return super(FOIRequest, self).clean(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('foirequest_detail', args=[self.protocol])

    def __str__(self):
        return self.protocol

    @property
    def public_body(self):
        if self.first_message:
            return self.first_message.receiver

    @property
    def esic(self):
        if self.public_body:
            return self.public_body.esic

    @property
    def summary(self):
        if self.first_message:
            return self.first_message.summary

    @property
    def status(self):
        last_message = self.last_message
        status = None

        if not last_message:
            status = self.STATUS.waiting_user
        elif not last_message.is_from_user:
            appeal_deadline = timezone.now() - timezone.timedelta(days=self.APPEAL_DAYS)
            if last_message.sent_at <= appeal_deadline:
                status = self.STATUS.finished
            else:
                status = self.STATUS.waiting_user
            pass
        elif last_message.is_sent:
            reply_deadline = timezone.now() - timezone.timedelta(days=self.REPLY_DAYS)
            if last_message.sent_at <= reply_deadline:
                status = self.STATUS.delayed
            else:
                status = self.STATUS.waiting_government
        else:
            status = last_message.status

        return status

    @property
    def moderation_message(self):
        first_message = self.first_message
        if first_message:
            return first_message.moderation_message

    @property
    def first_message(self):
        return self.message_set.order_by('created_at').first()

    @property
    def last_message(self):
        return self.message_set.order_by('created_at').last()


class Message(models.Model):
    class STATUS(enum.Enum):
        pending = _('Pending moderation')
        rejected = _('Rejected')
        ready = _('Ready to be sent')
        sent = _('Sent')

    foi_request = models.ForeignKey(FOIRequest, on_delete=models.CASCADE)
    sender = models.ForeignKey(
        PublicBody,
        null=True,
        blank=True,
        related_name='messages_sent',
        on_delete=models.PROTECT
    )
    receiver = models.ForeignKey(
        PublicBody,
        null=True,
        blank=True,
        related_name='messages_received',
        on_delete=models.PROTECT
    )
    summary = models.TextField(blank=True)
    body = models.TextField(blank=False)
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Sent date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Moderation-related attributes
    moderation_status = models.NullBooleanField(
        choices=(
            (None, 'Pending'),
            (True, 'Approved'),
            (False, 'Rejected'),
        )
    )
    moderation_message = models.TextField(blank=True)
    moderated_at = models.DateTimeField(null=True, blank=True)

    @property
    def status(self):
        status = None

        if self.is_pending_moderation:
            status = self.STATUS.pending
        elif self.is_rejected:
            status = self.STATUS.rejected
        elif not self.is_sent:
            status = self.STATUS.ready
        else:
            status = self.STATUS.sent

        return status

    @property
    def sender_type(self):
        sender_type = 'user'
        if self.sender is not None:
            sender_type = 'government'
        return sender_type

    def __str__(self):
        summary = self.summary
        if not summary:
            summary = self.body[0:100]

        return '(%s) %s' % (self.sender_type, summary)

    def _attached_file_path(self, filename):
        root, ext = os.path.splitext(filename)
        hash_size = 24

        hasher = hashlib.sha256()
        hasher.update(root.encode('utf-8'))
        hashed_filename = '{}{}'.format(hasher.hexdigest()[:hash_size], ext)

        return hashed_filename

    attached_file = models.FileField(
        upload_to=_attached_file_path,
        blank=True,
        null=True
    )

    @property
    def is_from_user(self):
        return self.sender is None

    @property
    def is_approved(self):
        return self.moderation_status is True

    @property
    def is_rejected(self):
        return self.moderation_status is False

    @property
    def is_pending_moderation(self):
        return self.moderation_status is None

    @property
    def is_sent(self):
        return self.sent_at is not None

    class Meta:
        ordering = ['-created_at', '-moderation_status']

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self._original_moderation_status = self.moderation_status

    def save(self, *args, **kwargs):
        self.clean()
        return super(Message, self).save(*args, **kwargs)

    def clean(self):
        self._update_moderated_at_if_needed()

        if self.sender and self.receiver:
            msg = _('Message can either have a "sender" or a "receiver", not both.')
            raise ValidationError({
                'sender': msg,
                'receiver': msg,
            })

        if not self.is_from_user:
            # Government messages are automatically approved
            if not self.moderation_status:
                self.approve()
            if not self.sent_at:
                raise ValidationError({
                    'sent_at': _('Government messages must have a "sent_at" date.'),
                })

        if self.is_from_user and not self.is_approved:
            if self.sent_at is not None:
                raise ValidationError({
                    'sent_at': _('Only approved user messages can be marked as sent.'),
                })

        if self.is_rejected and not self.moderation_message:
            raise ValidationError({
                'moderation_status': _('A message can not be rejected without an explanation.'),  # noqa: E501
            })

    def approve(self):
        self.moderated_at = timezone.now()
        self.moderation_status = True

    def reject(self):
        self.moderated_at = timezone.now()
        self.moderation_status = False

    def get_absolute_url(self):
        return self.foi_request.get_absolute_url()

    def _update_moderated_at_if_needed(self):
        if self._original_moderation_status != self.moderation_status:
            self.moderated_at = timezone.now()
            self._original_moderation_status = self.moderation_status
