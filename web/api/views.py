from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from web.foi_requests.forms import FOIRequestForm
from web.foi_requests.models import PublicBody

from .authentication import ApiTokenRequiredMixin
from .forms import ApiMessageForm


@method_decorator(csrf_exempt, name="dispatch")
class CreateFOIRequestApiView(ApiTokenRequiredMixin, View):
    def post(self, request):
        data = request.POST.copy()
        data.setdefault("can_publish", "true")

        message_form = ApiMessageForm(data, request.FILES)
        foi_request_form = FOIRequestForm(data)

        if not (message_form.is_valid() and foi_request_form.is_valid()):
            errors = {
                **message_form.errors.get_json_data(),
                **foi_request_form.errors.get_json_data(),
            }
            return JsonResponse(
                {"erro": "Dados inválidos.", "detalhes": errors}, status=400
            )

        with transaction.atomic():
            foi_request = foi_request_form.save()
            message_form.instance.foi_request = foi_request
            message_form.save()

        return JsonResponse(
            {
                "protocol": foi_request.protocol,
                "url": request.build_absolute_uri(foi_request.get_absolute_url()),
                "status": foi_request.status.name,
            },
            status=201,
        )


class PublicBodySearchApiView(ApiTokenRequiredMixin, View):
    MAX_RESULTS = 20

    def get(self, request):
        search = request.GET.get("search", "").strip()

        queryset = PublicBody.objects.all()
        if search:
            queryset = queryset.filter(name__icontains=search)

        results = [
            {
                "id": public_body.id,
                "name": public_body.name,
                "level": public_body.level,
                "municipality": public_body.municipality,
                "uf": public_body.uf,
            }
            for public_body in queryset[: self.MAX_RESULTS]
        ]

        return JsonResponse({"results": results})
