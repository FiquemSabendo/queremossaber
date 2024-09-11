import json
import pytest
from django.urls import reverse

from ..views import WhoamiView


class TestWhoamiView:
    URL = reverse("whoami_get")

    @pytest.mark.parametrize(
        "header",
        (
            "REMOTE_ADDR",
            "HTTP_X_FORWARDED_FOR",
            "HTTP_X_REAL_IP",
            "HTTP_USER_AGENT",
        ),
    )
    def test_get_returns_header(self, rf, header):
        request = rf.get(self.URL, **{header: "foobar"})

        response = WhoamiView.as_view()(request)

        data = json.loads(response.content)
        assert data.get(header) == "foobar"
