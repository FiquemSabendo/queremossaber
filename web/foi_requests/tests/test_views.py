import pytest
from django.urls import reverse

from ..models import PublicBody
from ..views import FOIRequestRedirectView, CreatePublicBodyView


class TestFOIRequestRedirectView(object):
    def test_redirects_to_foirequest_detail(self, rf):
        protocol = 'ABC'
        expected_url = reverse('foirequest_detail', kwargs={'slug': protocol})

        request = rf.get('?protocol=' + protocol)
        response = FOIRequestRedirectView.as_view()(request)

        assert response.url == expected_url


class TestCreatePublicBodyView(object):
    @pytest.mark.django_db()
    def test_form_valid_adds_created_esic_to_public_body(self, rf):
        # FIXME: be more intelligent on how to set the URL and params
        name = 'public body name'
        url = 'http://example.com'
        request = rf.post('/p/public_body/new/', {
            'url': url,
            'name': name,
        })

        CreatePublicBodyView.as_view()(request)

        public_body = PublicBody.objects.filter(name=name).first()
        assert public_body is not None
        assert public_body.esic.url == url
