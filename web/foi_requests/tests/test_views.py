from django.urls import reverse

from ..views import FOIRequestRedirectView


class TestFOIRequestRedirectView(object):
    def test_redirects_to_foirequest_detail(self, rf):
        protocol = 'ABC'
        expected_url = reverse('foirequest_detail', kwargs={'slug': protocol})

        request = rf.get('?protocol=' + protocol)
        response = FOIRequestRedirectView.as_view()(request)

        assert response.url == expected_url
