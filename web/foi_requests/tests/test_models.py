import pytest
from django.urls import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone

from ..models import Message, FOIRequest, Esic, PublicBody


class TestMessage(object):
    @pytest.mark.django_db()
    def test_creating_message_creates_foi_request(self):
        message = Message()
        message.save()

        assert message.foi_request

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

    @pytest.mark.django_db()
    def test_absolute_url_points_to_foi_request_url(self):
        message = Message()
        message.save()
        expected_url = reverse(
            'foirequest_detail',
            args=[message.foi_request.protocol]
        )

        assert message.get_absolute_url() == expected_url

    @pytest.mark.django_db()
    def test_message_updates_moderated_at_when_moderation_status_is_set(self):
        message = Message(moderated_at=None)
        assert message.moderated_at is None

        with transaction.atomic():
            message.moderation_status = True
            message.save()

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

    def test_message_is_automatically_approved_when_sender_is_government(self, message_from_government):
        assert not message_from_government.is_from_user
        message_from_government.moderation_status = None

        message_from_government.clean()

        assert message_from_government.is_approved

    def test_message_is_not_automatically_approved_when_sender_is_user(self, message_from_user):
        assert message_from_user.is_from_user
        message_from_user.moderation_status = None

        message_from_user.clean()

        assert not message_from_user.is_approved


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
    def test_public_body_returns_first_messages_receiver(self, public_body):
        # FIXME: The knowledge of saving the esic shouldn't be here. Ideally,
        # the public_body received would already be saved.
        public_body.esic.save()
        public_body.save()

        with transaction.atomic():
            foi_request = FOIRequest()
            first_message = Message(foi_request=foi_request, receiver=public_body)
            last_message = Message(foi_request=foi_request, receiver=None)

            foi_request.save()
            first_message.save()
            last_message.save()

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


@pytest.fixture
def public_body(esic):
    return PublicBody(
        name='example',
        esic=esic
    )


@pytest.fixture
def esic():
    return Esic(
        url='http://example.com'
    )


@pytest.fixture
def foi_request():
    return FOIRequest()


@pytest.fixture
def message_from_user(public_body):
    return Message(
        sender=None,
        receiver=public_body
    )


@pytest.fixture
def message_from_government(public_body):
    return Message(
        sender=public_body,
        receiver=None
    )
