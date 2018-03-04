import pytest
from django.urls import reverse
from django.db import transaction
from django.db.utils import IntegrityError

from ..models import Message, FOIRequest, PublicBody


@pytest.mark.django_db()
class TestMessage(object):
    def test_creating_message_creates_foi_request(self):
        message = Message()
        message.save()

        assert message.foi_request

    def test_foi_request_isnt_created_if_message_creation_fails(self):
        initial_foi_requests_count = FOIRequest.objects.count()
        message = Message()
        message.body = None

        with transaction.atomic():
            with pytest.raises(IntegrityError):
                message.save()

        assert initial_foi_requests_count == FOIRequest.objects.count()

    def test_absolute_url_points_to_foi_request_url(self):
        message = Message()
        message.save()
        expected_url = reverse(
            'foirequest_detail',
            args=[message.foi_request.protocol]
        )

        assert message.get_absolute_url() == expected_url


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


@pytest.fixture
def public_body():
    return PublicBody(
        name='example',
        esic_url='http://example.com'
    )
