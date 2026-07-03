import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from web.foi_requests.models import FOIRequest, PublicBody
from web.foi_requests.tests.conftest import save_public_body


class TestCreateFOIRequestApiView:
    URL = reverse("api_foi_request_create")

    @pytest.mark.django_db()
    def test_requires_authentication(self, client):
        response = client.post(self.URL, {})

        assert response.status_code == 401

    @pytest.mark.django_db()
    def test_rejects_invalid_token(self, client):
        response = client.post(self.URL, {}, HTTP_AUTHORIZATION="Token invalid")

        assert response.status_code == 401

    @pytest.mark.django_db()
    def test_returns_validation_errors_for_invalid_data(self, client, auth_headers):
        response = client.post(self.URL, {}, **auth_headers)

        assert response.status_code == 400
        assert "detalhes" in response.json()

    @pytest.mark.django_db()
    def test_creates_foi_request_and_message_pending_moderation(
        self, client, auth_headers, public_body
    ):
        save_public_body(public_body)

        data = {
            "receiver": public_body.pk,
            "summary": "summary",
            "body": "body" * 20,
        }

        response = client.post(self.URL, data, **auth_headers)

        assert response.status_code == 201
        payload = response.json()

        foi_request = FOIRequest.objects.get(protocol=payload["protocol"])
        message = foi_request.first_message
        assert foi_request.can_publish is True
        assert message.receiver_id == public_body.pk
        assert message.body == data["body"]
        assert message.is_pending_moderation

    @pytest.mark.django_db()
    def test_accepts_attached_file(
        self, client, auth_headers, public_body, settings, tmp_path
    ):
        settings.MEDIA_ROOT = str(tmp_path)
        save_public_body(public_body)
        upload = SimpleUploadedFile(
            "mapa.png", b"fake-image-bytes", content_type="image/png"
        )

        data = {
            "receiver": public_body.pk,
            "summary": "summary",
            "body": "body" * 20,
            "attached_file": upload,
        }

        response = client.post(self.URL, data, **auth_headers)

        assert response.status_code == 201
        foi_request = FOIRequest.objects.get(protocol=response.json()["protocol"])
        assert foi_request.first_message.attached_file.name.endswith(".png")

    @pytest.mark.django_db()
    def test_respects_explicit_can_publish_false(
        self, client, auth_headers, public_body
    ):
        save_public_body(public_body)

        data = {
            "receiver": public_body.pk,
            "summary": "summary",
            "body": "body" * 20,
            "can_publish": False,
        }

        response = client.post(self.URL, data, **auth_headers)

        assert response.status_code == 201
        foi_request = FOIRequest.objects.get(protocol=response.json()["protocol"])
        assert foi_request.can_publish is False


class TestPublicBodySearchApiView:
    URL = reverse("api_public_body_search")

    @pytest.mark.django_db()
    def test_requires_authentication(self, client):
        response = client.get(self.URL)

        assert response.status_code == 401

    @pytest.mark.django_db()
    def test_filters_by_search_term(self, client, auth_headers):
        PublicBody(name="Prefeitura de Sao Paulo").save()
        PublicBody(name="Ministerio da Saude").save()

        response = client.get(self.URL, {"search": "Sao Paulo"}, **auth_headers)

        assert response.status_code == 200
        names = [result["name"] for result in response.json()["results"]]
        assert names == ["Prefeitura de Sao Paulo"]

    @pytest.mark.django_db()
    def test_returns_all_when_no_search_term(self, client, auth_headers):
        PublicBody(name="Prefeitura de Sao Paulo").save()
        PublicBody(name="Ministerio da Saude").save()

        response = client.get(self.URL, **auth_headers)

        assert response.status_code == 200
        assert len(response.json()["results"]) == 2
