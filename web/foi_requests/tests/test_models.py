import pytest
from django.urls import reverse
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from ..models import Message, FOIRequest, PublicBody


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

    def test_is_from_user_is_true_if_sender_is_none(self):
        message = Message(sender=None)

        assert message.is_from_user

    def test_is_from_user_is_false_if_sender_is_not_none(self):
        public_body = PublicBody()
        message = Message(sender=public_body)

        assert not message.is_from_user


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
        with transaction.atomic():
            public_body.save()
            message = Message(receiver=public_body)
            message.save()
        foi_request = message.foi_request

        assert foi_request.public_body == message.receiver

    def test_public_body_returns_none_if_there_are_no_messages(self):
        assert FOIRequest().public_body is None

    @pytest.mark.django_db()
    def test_foi_request_updates_moderated_at_when_moderation_status_is_set(self, foi_request):
        assert foi_request.moderated_at is None

        with transaction.atomic():
            foi_request.moderation_status = True
            foi_request.save()

        assert foi_request.moderated_at is not None

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
def public_body():
    return PublicBody(
        name='example',
        esic_url='http://example.com'
    )


@pytest.fixture
def foi_request():
    return FOIRequest()
