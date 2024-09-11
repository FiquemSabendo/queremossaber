import pytest

from ..management.commands.load_public_bodies_and_esics import (
    _create_or_update_public_body_and_esic,
)


class TestLoadPublicBodiesAndEsicsCommand(object):
    @pytest.mark.django_db()
    def test_create_or_update_public_body_and_esic(self, esic_data):
        public_body = _create_or_update_public_body_and_esic(esic_data)

        assert public_body.name == esic_data["orgao"]
        assert public_body.uf == esic_data["uf"]
        assert public_body.municipality == esic_data["municipio"]
        assert public_body.esic.url == esic_data["url"]

        is_saved = lambda model: model.pk is not None  # noqa: E731
        assert is_saved(public_body)
        assert is_saved(public_body.esic)


@pytest.fixture
def esic_data():
    return {
        "orgao": "ACME Inc",
        "uf": "DF",
        "municipio": "Brasília",
        "cod_ibge": "5300108",
        "url": "http://www.example.com",
    }
