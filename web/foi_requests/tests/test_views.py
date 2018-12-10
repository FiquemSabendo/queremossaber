import pytest
from django.urls import reverse

from ..models import PublicBody
from ..views import FOIRequestRedirectView, CreatePublicBodyView, CreateFOIRequestView
from .conftest import save_public_body


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


class TestCreateFOIRequestView():
    URL = reverse('foi_request_new')

    def test_context_data_contains_message_and_foi_request_forms(self):
        context = CreateFOIRequestView().get_context_data()

        assert 'message_form' in context
        assert 'foi_request_form' in context

    def test_get_passes_receiver_parameter_to_message_form(self, rf):
        params = {'receiver': '51'}
        request = rf.get(self.URL, params)

        response = CreateFOIRequestView.as_view()(request)

        message_form = response.context_data['message_form']
        assert message_form.initial.get('receiver') == params['receiver']

    @pytest.mark.django_db()
    def test_post_validates_message_form(self, client):
        # foi_request_form is always valid, so we don't need to test it
        response = client.post(self.URL)

        message_form = response.context[-1]['message_form']
        assert not message_form.is_valid()

    @pytest.mark.django_db()
    def test_post_creates_foi_request_and_message_and_redirects_to_foi_request_page(self, public_body, client):
        save_public_body(public_body)

        context = {
            'receiver': public_body.pk,
            'summary': 'summary',
            'body': 'body' * 100,
            'can_publish': True,
        }

        response = client.post(self.URL, context, follow=True)

        foi_request = response.context[-1]['object']
        message = foi_request.first_message
        assert foi_request.can_publish is context['can_publish']
        assert message.receiver_id == context['receiver']
        assert message.summary == context['summary']
        assert message.body == context['body']
