from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView

from .forms import MessageForm
from .models import FOIRequest


class CreateMessageView(CreateView):
    form_class = MessageForm
    template_name = 'foi_requests/message_new.html'


class FOIRequestView(DetailView):
    model = FOIRequest
    slug_field = 'protocol'
