from django.views import View
from django.http import JsonResponse


class WhoamiView(View):
    def get(self, request):
        headers_to_keep = set(
            (
                "REMOTE_ADDR",
                "HTTP_X_FORWARDED_FOR",
                "HTTP_X_REAL_IP",
                "HTTP_USER_AGENT",
            )
        )
        http_headers = {
            key: value
            for (key, value) in request.META.items()
            if key in headers_to_keep
        }
        return JsonResponse(http_headers)
