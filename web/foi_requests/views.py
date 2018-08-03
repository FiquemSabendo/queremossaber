from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.urls import reverse

from .forms import MessageForm, EsicForm
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
    ]

    def get_context_data(self, **kwargs):
        data = super(CreatePublicBodyView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['esic_form'] = EsicForm(self.request.POST)
        else:
            data['esic_form'] = EsicForm()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        esic_form = context['esic_form']

        if esic_form.is_valid():
            # TODO: Add transactionwith transaction.commit_on_success():
            esic_form.save()
            form.instance.esic = esic_form.instance
            self.object = form.save()

        return super(CreatePublicBodyView, self).form_valid(form)

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
