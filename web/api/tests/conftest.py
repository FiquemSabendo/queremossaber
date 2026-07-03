import pytest

from web.foi_requests.models import Esic, PublicBody

from ..models import ApiClient


@pytest.fixture
def esic():
    return Esic(url="http://example.com")


@pytest.fixture
def public_body(esic):
    return PublicBody(name="Prefeitura de Exemplo", esic=esic)


@pytest.fixture
def api_client_model():
    return ApiClient.objects.create(name="iluminando")


@pytest.fixture
def auth_headers(api_client_model):
    return {"HTTP_AUTHORIZATION": "Token {}".format(api_client_model.token)}
