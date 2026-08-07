from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse, NoReverseMatch
from django.db import transaction
from django.db.models import OuterRef, Subquery

from .forms import MessageForm, EsicForm, PublicBodyForm, FOIRequestForm
from .models import FOIRequest, Message, PublicBody


class CreateMessageView(CreateView):
    form_class = MessageForm
    template_name = "foi_requests/foi_request_new.html"

    def get_initial(self):
        return {
            "receiver": self.request.GET.get("receiver"),
        }


# Desabilita cache para não cachearmos o CSRF token
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
            "foi_request_creation_suspended": settings.SUSPEND_FOI_REQUEST_CREATION,
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


# Desabilita cache para não cachearmos o CSRF token
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["foi_request_creation_suspended"] = (
            settings.SUSPEND_FOI_REQUEST_CREATION
        )
        return context


class FOIRequestListView(ListView):
    """Lists the FOI requests whose authors allowed their publication.

    Also answers the protocol search: `?protocol=X` redirects to that
    request's page.
    """

    model = FOIRequest
    paginate_by = 50

    def get(self, request, *args, **kwargs):
        protocol = request.GET.get("protocol", "").strip()
        if protocol:
            try:
                return redirect("foirequest_detail", slug=protocol, permanent=True)
            except NoReverseMatch:
                # Protocols only have letters and digits, so anything else
                # can't be an existing request.
                raise Http404
        return super(FOIRequestListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FOIRequestListView, self).get_context_data(**kwargs)

        # Elides the page numbers far from the current one, so the pagination
        # doesn't overflow the layout.
        context["page_range"] = context["paginator"].get_elided_page_range(
            context["page_obj"].number, on_each_side=1, on_ends=1
        )

        return context

    def get_queryset(self):
        # `public_body` and `summary` are properties that query the first
        # message, so we annotate them here to avoid one query per request.
        first_message = Message.objects.filter(foi_request=OuterRef("pk")).order_by(
            "created_at"
        )

        return (
            FOIRequest.objects.filter(can_publish=True)
            .annotate(
                first_message_moderation_status=Subquery(
                    first_message.values("moderation_status")[:1]
                ),
                public_body_name=Subquery(first_message.values("receiver__name")[:1]),
                first_message_summary=Subquery(first_message.values("summary")[:1]),
            )
            .filter(first_message_moderation_status=True)
            # The request's page shows every message, including the ones the
            # moderation rejected or hasn't reviewed yet. Listing it here would
            # make that content findable by anyone, so we only list requests
            # whose messages are all approved.
            .exclude(message__moderation_status__isnull=True)
            .exclude(message__moderation_status=False)
            .order_by("-created_at")
        )
