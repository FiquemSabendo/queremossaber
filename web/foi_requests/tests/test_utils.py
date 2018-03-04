from .. import utils


class TestGenerateProtocol(object):
    def test_returns_random_protocol(self):
        assert utils.generate_protocol() != utils.generate_protocol()

    def test_defaults_to_8_characters(self):
        assert len(utils.generate_protocol()) == 8

    def test_accept_different_length_as_parameter(self):
        assert len(utils.generate_protocol(15)) == 15
