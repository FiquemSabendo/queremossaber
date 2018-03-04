from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from .forms import MessageForm


class IndexView(TemplateView):
    template_name = 'foi_requests/index.html'


class CreateMessageView(CreateView):
    form_class = MessageForm
    template_name = 'foi_requests/message_new.html'
