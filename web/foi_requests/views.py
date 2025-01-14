from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from .forms import MessageForm, EsicForm, PublicBodyForm, FOIRequestForm
from .models import FOIRequest, PublicBody


class CreateMessageView(CreateView):
    form_class = MessageForm
    template_name = "foi_requests/foi_request_new.html"

    def get_initial(self):
        return {
            "receiver": self.request.GET.get("receiver"),
        }


# Disabilita cache para não cachearmos o CSRF token
@method_decorator(never_cache, name="dispatch")
class CreateFOIRequestView(TemplateView):
    template_name = "foi_requests/foi_request_new.html"

    def get_context_data(self, **kwargs):
        context = super(CreateFOIRequestView, self).get_context_data(**kwargs)

        message_form_initial = {}

        if hasattr(self, "request"):
            message_form_initial["receiver"] = self.request.GET.get("receiver")

        forms = {
            "message_form": kwargs.get(
                "message_form", MessageForm(initial=message_form_initial)
            ),
            "foi_request_form": kwargs.get("foi_request_form", FOIRequestForm()),
        }

        return {**context, **forms}

    def post(self, request):
        message_form = MessageForm(request.POST)
        foi_request_form = FOIRequestForm(request.POST)
        context = {
            "message_form": message_form,
            "foi_request_form": foi_request_form,
        }

        if all([message_form.is_valid(), foi_request_form.is_valid()]):
            with transaction.atomic():
                foi_request = foi_request_form.save()
                message_form.instance.foi_request = foi_request
                message_form.save()
                return redirect(foi_request)

        return render(request, self.template_name, context)


# Disabilita cache para não cachearmos o CSRF token
@method_decorator(never_cache, name="dispatch")
class CreatePublicBodyView(CreateView):
    form_class = PublicBodyForm
    model = PublicBody

    def get_context_data(self, **kwargs):
        data = super(CreatePublicBodyView, self).get_context_data(**kwargs)
        if self.request.POST:
            data["esic_form"] = EsicForm(self.request.POST)
        else:
            data["esic_form"] = EsicForm()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        esic_form = context["esic_form"]

        if esic_form.is_valid():
            # TODO: Add transactionwith transaction.commit_on_success():
            esic_form.save()
            form.instance.esic = esic_form.instance
            self.object = form.save()

        return super(CreatePublicBodyView, self).form_valid(form)

    def get_success_url(self):
        return "{url}?receiver={receiver}".format(
            url=reverse("foi_request_new"), receiver=self.object.id
        )


class FOIRequestView(DetailView):
    model = FOIRequest
    slug_field = "protocol"


class FOIRequestRedirectView(RedirectView):
    pattern_name = "foirequest_search"
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        protocol = self.request.GET.get("protocol")
        return reverse("foirequest_detail", kwargs={"slug": protocol})
