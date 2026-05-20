import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone

from ..models import FOIRequest, Message
from .conftest import save_message, save_public_body


@pytest.fixture(autouse=True)
def clear_view_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def published_request_with_gov_message(foi_request, message_from_government):
    foi_request.can_publish = True
    message_from_government.foi_request = foi_request
    save_message(message_from_government)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def unpublishable_request_with_gov_message(message_from_government):
    foi_request = FOIRequest(can_publish=False)
    message_from_government.foi_request = foi_request
    save_message(message_from_government)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def published_request_without_gov_message(foi_request_with_sent_user_message):
    return foi_request_with_sent_user_message


def _create_gov_message(foi_request, public_body, **overrides):
    """Create a government Message, bypassing Message.clean() via .update()
    so we can synthesize edge cases (pending, rejected, unsent) that the
    model normally auto-corrects."""
    save_public_body(public_body)
    foi_request.save()
    message = Message.objects.create(
        foi_request=foi_request,
        sender=public_body,
        body="reply",
        sent_at=timezone.now(),
        moderation_status=True,
    )
    if overrides:
        Message.objects.filter(pk=message.pk).update(**overrides)
    return message


@pytest.fixture
def request_with_pending_gov_message(foi_request, public_body):
    # DB constraint only_approved_messages_can_have_sent_at forces sent_at=None
    # whenever moderation_status is not True.
    _create_gov_message(foi_request, public_body, moderation_status=None, sent_at=None)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_with_rejected_gov_message(foi_request, public_body):
    _create_gov_message(
        foi_request,
        public_body,
        moderation_status=False,
        sent_at=None,
        moderation_message="rejected for testing",
    )
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_with_unsent_gov_message(foi_request, public_body):
    _create_gov_message(foi_request, public_body, sent_at=None)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_with_multiple_gov_messages(foi_request, public_body):
    for _ in range(3):
        _create_gov_message(foi_request, public_body)
    foi_request.refresh_from_db()
    return foi_request


@pytest.fixture
def request_with_mixed_gov_messages(foi_request, public_body):
    foi_request.can_publish = True
    _create_gov_message(foi_request, public_body)
    _create_gov_message(
        foi_request,
        public_body,
        moderation_status=False,
        sent_at=None,
        moderation_message="rejected",
    )
    foi_request.refresh_from_db()
    return foi_request


class TestSitemap(object):
    @pytest.mark.django_db()
    def test_sitemap_responds_200_xml(self, client):
        response = client.get(reverse("sitemap"))
        assert response.status_code == 200
        assert response["Content-Type"].startswith("application/xml")

    @pytest.mark.django_db()
    def test_sitemap_includes_static_pages(self, client):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert reverse("index") in body
        assert reverse("faq") in body

    @pytest.mark.django_db()
    def test_includes_publishable_request_answered_by_public_body(
        self, client, published_request_with_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert published_request_with_gov_message.get_absolute_url() in body

    @pytest.mark.django_db()
    def test_excludes_request_with_can_publish_false(
        self, client, unpublishable_request_with_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert unpublishable_request_with_gov_message.get_absolute_url() not in body

    @pytest.mark.django_db()
    def test_excludes_request_without_message_from_public_body(
        self, client, published_request_without_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert published_request_without_gov_message.get_absolute_url() not in body

    @pytest.mark.django_db()
    def test_excludes_request_with_pending_gov_message(
        self, client, request_with_pending_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert request_with_pending_gov_message.get_absolute_url() not in body

    @pytest.mark.django_db()
    def test_excludes_request_with_rejected_gov_message(
        self, client, request_with_rejected_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert request_with_rejected_gov_message.get_absolute_url() not in body

    @pytest.mark.django_db()
    def test_excludes_request_with_unsent_gov_message(
        self, client, request_with_unsent_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert request_with_unsent_gov_message.get_absolute_url() not in body

    @pytest.mark.django_db()
    def test_request_with_multiple_gov_messages_appears_once(
        self, client, request_with_multiple_gov_messages
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        url = request_with_multiple_gov_messages.get_absolute_url()
        assert body.count(url) == 1

    @pytest.mark.django_db()
    def test_includes_request_with_mixed_qualifying_and_rejected_messages(
        self, client, request_with_mixed_gov_messages
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert request_with_mixed_gov_messages.get_absolute_url() in body

    @pytest.mark.django_db()
    def test_emits_lastmod_for_published_request(
        self, client, published_request_with_gov_message
    ):
        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        assert "<lastmod>" in body

    @pytest.mark.django_db()
    def test_uses_https_protocol(self, client, published_request_with_gov_message):
        import re

        response = client.get(reverse("sitemap"))
        body = response.content.decode("utf-8")
        loc_urls = re.findall(r"<loc>([^<]+)</loc>", body)
        assert loc_urls, "Expected at least one <loc> URL"
        for url in loc_urls:
            assert url.startswith("https://"), url


class TestRobotsTxt(object):
    @pytest.mark.django_db()
    def test_responds_200_text(self, client):
        response = client.get(reverse("robots_txt"))
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/plain")

    @pytest.mark.django_db()
    def test_references_sitemap_url(self, client):
        response = client.get(reverse("robots_txt"))
        body = response.content.decode("utf-8")
        assert "Sitemap:" in body
        assert reverse("sitemap") in body
