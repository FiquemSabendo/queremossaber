import pytest
from django.urls import reverse

from ..models import FOIRequest, Message
from ..views import FOIRequestListView
from .conftest import save_public_body


def _create_user_message(foi_request, public_body, **overrides):
    """Create a user Message, bypassing Message.clean() via .update() so we
    can synthesize states (pending, rejected) that the model normally
    auto-corrects."""
    save_public_body(public_body)
    foi_request.save()
    message = Message.objects.create(
        foi_request=foi_request,
        receiver=public_body,
        summary="resumo do pedido",
        body="corpo do pedido",
        moderation_status=True,
    )
    if overrides:
        Message.objects.filter(pk=message.pk).update(**overrides)
    return message


@pytest.fixture
def approved_request(foi_request, public_body):
    _create_user_message(foi_request, public_body)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def unpublishable_request(public_body):
    foi_request = FOIRequest(can_publish=False)
    _create_user_message(foi_request, public_body)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def pending_request(foi_request, public_body):
    _create_user_message(foi_request, public_body, moderation_status=None)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def rejected_request(foi_request, public_body):
    _create_user_message(
        foi_request,
        public_body,
        moderation_status=False,
        moderation_message="rejected for testing",
    )
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_with_pending_follow_up(foi_request, public_body):
    _create_user_message(foi_request, public_body)
    _create_user_message(foi_request, public_body, moderation_status=None)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_with_rejected_follow_up(foi_request, public_body):
    _create_user_message(foi_request, public_body)
    _create_user_message(
        foi_request,
        public_body,
        moderation_status=False,
        moderation_message="rejected for testing",
    )
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_approved_after_a_rejection(foi_request, public_body):
    _create_user_message(
        foi_request,
        public_body,
        moderation_status=False,
        moderation_message="rejected for testing",
    )
    _create_user_message(foi_request, public_body)
    foi_request.refresh_from_db()
    return foi_request


class TestFOIRequestListView(object):
    @pytest.mark.django_db()
    def test_includes_approved_request(self, client, approved_request):
        response = client.get(reverse("foirequest_list"))
        body = response.content.decode("utf-8")

        assert response.status_code == 200
        assert approved_request.protocol in body
        assert approved_request.public_body.name in body
        assert approved_request.summary in body

    @pytest.mark.django_db()
    def test_includes_approved_request_not_sent_to_public_body(
        self, client, approved_request
    ):
        assert approved_request.first_message.sent_at is None

        response = client.get(reverse("foirequest_list"))

        assert approved_request.protocol in response.content.decode("utf-8")

    @pytest.mark.django_db()
    def test_excludes_request_with_can_publish_false(
        self, client, unpublishable_request
    ):
        response = client.get(reverse("foirequest_list"))

        assert unpublishable_request.protocol not in response.content.decode("utf-8")

    @pytest.mark.django_db()
    def test_excludes_request_pending_moderation(self, client, pending_request):
        response = client.get(reverse("foirequest_list"))

        assert pending_request.protocol not in response.content.decode("utf-8")

    @pytest.mark.django_db()
    def test_excludes_rejected_request(self, client, rejected_request):
        response = client.get(reverse("foirequest_list"))

        assert rejected_request.protocol not in response.content.decode("utf-8")

    @pytest.mark.django_db()
    def test_excludes_request_with_message_pending_moderation(
        self, client, request_with_pending_follow_up
    ):
        # The request's page shows every message, so listing it would publish
        # a message the moderation hasn't reviewed yet.
        response = client.get(reverse("foirequest_list"))

        assert request_with_pending_follow_up.protocol not in response.content.decode(
            "utf-8"
        )

    @pytest.mark.django_db()
    def test_excludes_request_with_rejected_message(
        self, client, request_with_rejected_follow_up
    ):
        response = client.get(reverse("foirequest_list"))

        assert request_with_rejected_follow_up.protocol not in response.content.decode(
            "utf-8"
        )

    @pytest.mark.django_db()
    def test_excludes_request_whose_first_message_was_rejected(
        self, client, request_approved_after_a_rejection
    ):
        response = client.get(reverse("foirequest_list"))

        assert (
            request_approved_after_a_rejection.protocol
            not in response.content.decode("utf-8")
        )

    @pytest.mark.django_db()
    def test_orders_by_most_recent_first(self, client, public_body):
        older = FOIRequest()
        _create_user_message(older, public_body)
        newer = FOIRequest()
        _create_user_message(newer, public_body)

        response = client.get(reverse("foirequest_list"))

        listed = [
            foi_request.protocol
            for foi_request in response.context["paginator"].object_list
        ]
        assert listed == [newer.protocol, older.protocol]

    @pytest.mark.django_db()
    def test_paginates_results(self, client, public_body):
        for _ in range(FOIRequestListView.paginate_by + 1):
            _create_user_message(FOIRequest(), public_body)

        first_page = client.get(reverse("foirequest_list"))
        second_page = client.get(reverse("foirequest_list") + "?page=2")

        assert len(first_page.context["foirequest_list"]) == (
            FOIRequestListView.paginate_by
        )
        assert len(second_page.context["foirequest_list"]) == 1

    @pytest.mark.django_db()
    def test_queries_dont_grow_with_number_of_requests(
        self, client, public_body, django_assert_num_queries
    ):
        _create_user_message(FOIRequest(), public_body)
        with django_assert_num_queries(2) as captured:
            client.get(reverse("foirequest_list"))

        for _ in range(3):
            _create_user_message(FOIRequest(), public_body)
        with django_assert_num_queries(len(captured)):
            client.get(reverse("foirequest_list"))

    @pytest.mark.django_db()
    def test_redirects_protocol_search_to_foirequest_detail(self, client):
        protocol = "ABC"

        response = client.get(reverse("foirequest_list"), {"protocol": protocol})

        assert response.status_code == 301
        assert response.url == reverse("foirequest_detail", kwargs={"slug": protocol})

    @pytest.mark.django_db()
    def test_protocol_search_with_invalid_characters_is_not_found(self, client):
        response = client.get(reverse("foirequest_list"), {"protocol": "AB C/../"})

        assert response.status_code == 404

    @pytest.mark.django_db()
    def test_empty_protocol_search_shows_the_list(self, client, approved_request):
        response = client.get(reverse("foirequest_list"), {"protocol": " "})

        assert response.status_code == 200
        assert approved_request.protocol in response.content.decode("utf-8")
