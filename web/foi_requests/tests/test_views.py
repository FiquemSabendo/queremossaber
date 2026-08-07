import pytest
from django.test import override_settings
from django.urls import reverse

from ..models import PublicBody
from ..views import CreatePublicBodyView, CreateFOIRequestView
from .conftest import save_message, save_public_body


class TestCreatePublicBodyView(object):
    @pytest.mark.django_db()
    def test_form_valid_adds_created_esic_to_public_body(self, rf):
        # FIXME: be more intelligent on how to set the URL and params
        name = "public body name"
        url = "http://example.com"
        request = rf.post(
            "/p/public_body/new/",
            {
                "url": url,
                "name": name,
                "level": "Federal",
            },
        )

        CreatePublicBodyView.as_view()(request)

        public_body = PublicBody.objects.filter(name=name).first()
        assert public_body is not None
        assert public_body.esic.url == url


class TestCreateFOIRequestView:
    URL = reverse("foi_request_new")

    @override_settings(SUSPEND_FOI_REQUEST_CREATION=False)
    def test_get_shows_form_when_creation_is_not_suspended(self, rf):
        request = rf.get(self.URL)
        response = CreateFOIRequestView.as_view()(request)
        response.context_data["message_form"].fields[
            "receiver"
        ].queryset = PublicBody.objects.none()
        response.render()
        content = response.content.decode()

        assert 'name="summary"' in content
        assert "Não estamos recebendo novos pedidos" not in content

    @override_settings(SUSPEND_FOI_REQUEST_CREATION=True)
    def test_get_shows_warning_instead_of_form_when_creation_is_suspended(self, rf):
        request = rf.get(self.URL)
        response = CreateFOIRequestView.as_view()(request)
        response.render()
        content = response.content.decode()

        assert "Não estamos recebendo novos pedidos" in content
        assert 'name="summary"' not in content

    def test_context_data_contains_message_and_foi_request_forms(self):
        context = CreateFOIRequestView().get_context_data()

        assert "message_form" in context
        assert "foi_request_form" in context

    def test_get_passes_receiver_parameter_to_message_form(self, rf):
        params = {"receiver": "51"}
        request = rf.get(self.URL, params)

        response = CreateFOIRequestView.as_view()(request)

        message_form = response.context_data["message_form"]
        assert message_form.initial.get("receiver") == params["receiver"]

    @pytest.mark.django_db()
    def test_post_validates_message_form(self, client):
        # foi_request_form is always valid, so we don't need to test it
        response = client.post(self.URL)

        message_form = response.context[-1]["message_form"]
        assert not message_form.is_valid()

    @pytest.mark.django_db()
    def test_post_creates_foi_request_and_message_and_redirects_to_foi_request_page(
        self, public_body, client
    ):
        save_public_body(public_body)

        context = {
            "receiver": public_body.pk,
            "summary": "summary",
            "body": "body" * 100,
            "can_publish": True,
        }

        response = client.post(self.URL, context, follow=True)

        foi_request = response.context[-1]["object"]
        message = foi_request.first_message
        assert foi_request.can_publish is context["can_publish"]
        assert message.receiver_id == context["receiver"]
        assert message.summary == context["summary"]
        assert message.body == context["body"]


class TestFOIRequestView:
    NOTICE = "Este pedido aguarda envio"

    @pytest.mark.django_db()
    @override_settings(SUSPEND_FOI_REQUEST_CREATION=True)
    def test_shows_notice_for_unsent_request(self, client, message):
        save_message(message)

        response = client.get(message.foi_request.get_absolute_url())

        assert self.NOTICE in response.content.decode()

    @pytest.mark.django_db()
    @override_settings(SUSPEND_FOI_REQUEST_CREATION=True)
    def test_does_not_show_notice_for_sent_request(
        self, client, foi_request_with_sent_user_message
    ):
        response = client.get(foi_request_with_sent_user_message.get_absolute_url())

        assert self.NOTICE not in response.content.decode()

    @pytest.mark.django_db()
    @override_settings(SUSPEND_FOI_REQUEST_CREATION=True)
    def test_does_not_show_notice_for_rejected_request(self, client, message):
        message.moderation_message = "Rejeitado para teste"
        message.reject()
        save_message(message)

        response = client.get(message.foi_request.get_absolute_url())

        assert self.NOTICE not in response.content.decode()

    @pytest.mark.django_db()
    @override_settings(SUSPEND_FOI_REQUEST_CREATION=False)
    def test_does_not_show_notice_when_creation_is_not_suspended(self, client, message):
        save_message(message)

        response = client.get(message.foi_request.get_absolute_url())

        assert self.NOTICE not in response.content.decode()
