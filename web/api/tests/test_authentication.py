import pytest

from ..authentication import authenticate_request


class TestAuthenticateRequest:
    @pytest.mark.django_db()
    def test_returns_none_without_header(self, rf):
        request = rf.get("/")

        assert authenticate_request(request) is None

    @pytest.mark.django_db()
    def test_returns_none_with_wrong_prefix(self, rf):
        request = rf.get("/", HTTP_AUTHORIZATION="Bearer something")

        assert authenticate_request(request) is None

    @pytest.mark.django_db()
    def test_returns_none_for_unknown_token(self, rf):
        request = rf.get("/", HTTP_AUTHORIZATION="Token unknown")

        assert authenticate_request(request) is None

    @pytest.mark.django_db()
    def test_returns_none_for_inactive_client(self, rf, api_client_model):
        api_client_model.is_active = False
        api_client_model.save()
        auth_header = "Token {}".format(api_client_model.token)
        request = rf.get("/", HTTP_AUTHORIZATION=auth_header)

        assert authenticate_request(request) is None

    @pytest.mark.django_db()
    def test_returns_client_for_valid_token(self, rf, api_client_model):
        auth_header = "Token {}".format(api_client_model.token)
        request = rf.get("/", HTTP_AUTHORIZATION=auth_header)

        assert authenticate_request(request) == api_client_model
