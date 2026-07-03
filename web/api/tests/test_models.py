from ..models import ApiClient, generate_token


class TestApiClient:
    def test_str_returns_name(self):
        api_client = ApiClient(name="iluminando")

        assert str(api_client) == "iluminando"

    def test_token_is_auto_generated(self):
        api_client = ApiClient(name="iluminando")

        assert api_client.token
        assert len(api_client.token) == 40


class TestGenerateToken:
    def test_returns_unique_values(self):
        assert generate_token() != generate_token()
