from django.http import JsonResponse

from .models import ApiClient


def authenticate_request(request):
    """Retorna o ApiClient dono do token no header Authorization, ou None."""
    auth_header = request.headers.get("Authorization", "")
    prefix = "Token "
    if not auth_header.startswith(prefix):
        return None

    token = auth_header[len(prefix) :].strip()
    if not token:
        return None

    return ApiClient.objects.filter(token=token, is_active=True).first()


class ApiTokenRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        api_client = authenticate_request(request)
        if api_client is None:
            return JsonResponse(
                {"erro": "Token de autenticação inválido."}, status=401
            )

        request.api_client = api_client
        return super().dispatch(request, *args, **kwargs)
