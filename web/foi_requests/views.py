from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.urls import reverse

from .forms import MessageForm
from .models import FOIRequest


class CreateMessageView(CreateView):
    form_class = MessageForm
    template_name = 'foi_requests/message_new.html'


class FOIRequestView(DetailView):
    model = FOIRequest
    slug_field = 'protocol'


class FOIRequestRedirectView(RedirectView):
    pattern_name = 'foirequest_search'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        protocol = self.request.GET.get('protocol')
        return reverse('foirequest_detail', kwargs={'slug': protocol})
