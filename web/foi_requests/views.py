from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.urls import reverse

from .forms import MessageForm
from .models import FOIRequest, PublicBody


class CreateMessageView(CreateView):
    form_class = MessageForm
    template_name = 'foi_requests/message_new.html'

    def get_initial(self):
        return {
            'receiver': self.request.GET.get('receiver'),
        }


class CreatePublicBodyView(CreateView):
    model = PublicBody
    fields = [
        'name',
        'esic_url',
    ]

    def get_success_url(self):
        return '{url}?receiver={receiver}'.format(
            url=reverse('message_new'),
            receiver=self.object.id
        )


class FOIRequestView(DetailView):
    model = FOIRequest
    slug_field = 'protocol'


class FOIRequestRedirectView(RedirectView):
    pattern_name = 'foirequest_search'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        protocol = self.request.GET.get('protocol')
        return reverse('foirequest_detail', kwargs={'slug': protocol})
