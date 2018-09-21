import pytest
from django.db import transaction
from django.utils import timezone

from ..models import Message, FOIRequest, Esic, PublicBody


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
def message(foi_request):
    return Message(
        foi_request=foi_request
    )


@pytest.fixture
def foi_request_with_sent_user_message(foi_request, message_from_user):
    with transaction.atomic():
        message_from_user.approve()
        message_from_user.foi_request = foi_request
        message_from_user.sent_at = timezone.now()
        save_message(message_from_user)
    foi_request.refresh_from_db()
    return foi_request


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
        sent_at=timezone.now(),
        receiver=None
    )


def save_message(message):
    # FIXME: Ideally a simple message.save() would save everything, but I
    # couldn't find out how to do so in Django. Not yet.
    with transaction.atomic():
        if message.sender:
            save_public_body(message.sender)
            message.sender_id = message.sender.id
        if message.receiver:
            save_public_body(message.receiver)
            message.receiver_id = message.receiver.id
        message.foi_request.save()
        message.foi_request_id = message.foi_request.id
        message.save()


def save_public_body(public_body):
    with transaction.atomic():
        if public_body.esic:
            public_body.esic.save()
            public_body.esic_id = public_body.esic.id
        public_body.save()
    return public_body
