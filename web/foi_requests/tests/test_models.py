import pytest
from django.urls import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Message, FOIRequest, PublicBody
from .conftest import save_message


class TestMessage(object):
    @pytest.mark.django_db()
    def test_foi_request_isnt_created_if_message_creation_fails(self):
        initial_foi_requests_count = FOIRequest.objects.count()
        message = Message()
        message.body = None

        with transaction.atomic():
            with pytest.raises(IntegrityError):
                message.save()

        assert initial_foi_requests_count == FOIRequest.objects.count()

    @pytest.mark.django_db()
    def test_message_doesnt_create_new_foi_request_if_it_already_has_one(self, foi_request):
        foi_request.save()
        message = Message(foi_request=foi_request)
        message.save()

        assert message.foi_request == foi_request

    def test_get_absolute_url_points_to_foi_request_absolute_url(self, message):
        assert message.get_absolute_url() == message.foi_request.get_absolute_url()

    @pytest.mark.django_db()
    def test_message_updates_moderated_at_when_moderation_status_is_set(self, message):
        assert message.moderated_at is None

        message.moderation_status = True
        save_message(message)

        assert message.moderated_at is not None

    def test_message_non_approved_can_not_have_sent_at(self):
        message = Message(
            moderation_status=None,
            sent_at=timezone.now()
        )

        with pytest.raises(ValidationError):
            message.clean()

    def test_message_approved_can_have_sent_at(self):
        message = Message(
            moderation_status=True,
            sent_at=timezone.now()
        )

        message.clean()

    def test_message_approve_approves_the_message(self):
        message = Message(moderation_status=None)
        assert not message.is_approved

        message.approve()

        assert message.is_approved

    def test_message_reject_rejects_the_message(self):
        message = Message(moderation_status=None)
        assert not message.is_rejected

        message.reject()

        assert message.is_rejected

    def test_message_reject_fails_if_moderation_message_is_empty(self):
        message = Message(moderation_message='')

        message.clean()

        message.reject()

        with pytest.raises(ValidationError):
            message.clean()

    def test_is_from_user_is_true_if_sender_is_none(self):
        message = Message(sender=None)

        assert message.is_from_user

    def test_is_from_user_is_false_if_sender_is_not_none(self):
        public_body = PublicBody()
        message = Message(sender=public_body)

        assert not message.is_from_user

    def test_government_messages_must_have_sent_at(self, message_from_government):
        message_from_government.sent_at = None

        with pytest.raises(ValidationError) as excinfo:
            message_from_government.clean()

        assert 'sent_at' in excinfo.value.error_dict

    def test_message_is_automatically_approved_when_sender_is_government(self, message_from_government):
        message_from_government.moderation_status = None

        message_from_government.clean()

        assert message_from_government.is_approved

    def test_message_is_not_automatically_approved_when_sender_is_user(self, message_from_user):
        message_from_user.moderation_status = None

        message_from_user.clean()

        assert not message_from_user.is_approved

    def test_not_moderated_user_message_has_status_pending(self, message_from_user):
        message_from_user.moderation_status = None

        assert message_from_user.is_pending_moderation
        assert message_from_user.status == Message.STATUS.pending

    def test_rejected_user_message_has_status_rejected(self, message_from_user):
        message_from_user.reject()

        assert message_from_user.status == Message.STATUS.rejected

    def test_approved_unsent_user_message_has_status_ready(self, message_from_user):
        message_from_user.approve()
        message_from_user.sent_at = None

        assert message_from_user.status == Message.STATUS.ready

    def test_sent_user_message_has_status_sent(self, message_from_user):
        message_from_user.approve()
        message_from_user.sent_at = timezone.now()

        assert message_from_user.status == Message.STATUS.sent

    def test_attached_file_hashes_filename(self, message):
        filename = 'foo.pdf'
        expected_filename = '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae.pdf'

        generated_filename = message.attached_file.field.upload_to(message, filename)

        assert generated_filename.endswith(expected_filename)

    def test_message_cant_have_both_sender_and_receiver(self, message, public_body):
        message.sender = public_body
        message.receiver = public_body

        with pytest.raises(ValidationError) as excinfo:
            message.clean()

        assert 'sender' in excinfo.value.error_dict
        assert 'receiver' in excinfo.value.error_dict


class TestFOIRequest(object):
    def test_protocol_is_automatically_generated(self):
        foi_request = FOIRequest()

        assert foi_request.protocol is not None

    def test_protocol_is_unique(self):
        foi_request_1 = FOIRequest()
        foi_request_2 = FOIRequest()

        assert foi_request_1.protocol != foi_request_2.protocol

    def test_str_includes_protocol(self):
        foi_request = FOIRequest()

        assert foi_request.protocol in str(foi_request)

    @pytest.mark.django_db()
    def test_public_body_returns_first_messages_receiver(self, public_body, foi_request):
        first_message = Message(foi_request=foi_request, receiver=public_body)
        last_message = Message(foi_request=foi_request, receiver=None)

        save_message(first_message)
        save_message(last_message)

        assert foi_request.public_body == first_message.receiver

    def test_public_body_returns_none_if_there_are_no_messages(self):
        assert FOIRequest().public_body is None

    @pytest.mark.django_db()
    def test_protocol_cant_be_changed(self, foi_request):
        foi_request.save()
        original_protocol = foi_request.protocol

        with pytest.raises(ValidationError):
            foi_request.protocol = 'somethingelse'
            foi_request.save()

        foi_request.refresh_from_db()
        assert foi_request.protocol == original_protocol

    @pytest.mark.django_db()
    def test_last_message_returns_the_last_created_message(self, foi_request):
        first_message = Message(foi_request=foi_request)
        last_message = Message(foi_request=foi_request)

        save_message(first_message)
        save_message(last_message)

        foi_request.refresh_from_db()
        assert foi_request.last_message == last_message

    @pytest.mark.django_db()
    @pytest.mark.parametrize('sent_at,status', [
        (timezone.now() - timezone.timedelta(days=FOIRequest.REPLY_DAYS), FOIRequest.STATUS.delayed),
        (timezone.now() - timezone.timedelta(days=FOIRequest.REPLY_DAYS - 1), FOIRequest.STATUS.waiting_government),
    ])
    def test_status_last_message_is_sent_and_from_user(self, sent_at, status, foi_request_with_sent_user_message):
        last_message = foi_request_with_sent_user_message.last_message
        last_message.sent_at = sent_at
        last_message.save()

        assert status == foi_request_with_sent_user_message.status

    @pytest.mark.django_db()
    @pytest.mark.parametrize('sent_at,status', [
        (timezone.now() - timezone.timedelta(days=FOIRequest.APPEAL_DAYS), FOIRequest.STATUS.finished),
        (timezone.now() - timezone.timedelta(days=FOIRequest.APPEAL_DAYS - 1), FOIRequest.STATUS.waiting_user),
    ])
    def test_status_last_message_is_from_government(self, sent_at, status, foi_request, message_from_government):
        with transaction.atomic():
            foi_request.save()
            message_from_government.foi_request = foi_request
            message_from_government.sent_at = sent_at
            save_message(message_from_government)
        foi_request.refresh_from_db()

        assert not message_from_government.is_from_user
        assert status == foi_request.status

    def test_status_is_waiting_user_when_there_are_no_messages(self, foi_request):
        assert foi_request.last_message is None
        assert foi_request.status is FOIRequest.STATUS.waiting_user

    @pytest.mark.django_db()
    def test_summary_returns_first_messages_summary(self):
        foi_request = FOIRequest()

        with transaction.atomic():
            foi_request.save()
            first_message = Message(foi_request=foi_request, summary='First message')
            last_message = Message(foi_request=foi_request, summary='Last message')
            first_message.save()
            last_message.save()
            foi_request.message_set.set([first_message, last_message])

        assert foi_request.summary == first_message.summary

    def test_summary_returns_none_if_there_are_no_messages(self):
        assert FOIRequest().summary is None

    def test_get_absolute_url(self, foi_request):
        expected_url = reverse(
            'foirequest_detail',
            args=[foi_request.protocol]
        )

        assert foi_request.get_absolute_url() == expected_url
