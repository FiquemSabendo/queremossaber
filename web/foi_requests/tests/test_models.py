from django.test import TestCase
from django.db import transaction
from django.db.utils import IntegrityError

from ..models import Message, FOIRequest


class TestMessage(TestCase):
    def test_creating_message_creates_foi_request(self):
        message = Message()
        message.save()

        assert message.foi_request

    def test_foi_request_isnt_created_if_message_creation_fails(self):
        initial_foi_requests_count = FOIRequest.objects.count()
        message = Message()
        message.body = None

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                message.save()

        assert initial_foi_requests_count == FOIRequest.objects.count()


class TestFOIRequest(TestCase):
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
