from django.contrib.sitemaps import Sitemap
from django.db.models import Max, Q
from django.urls import reverse

from .models import FOIRequest


_QUALIFYING_MESSAGE = Q(
    message__sender__isnull=False,
    message__moderation_status=True,
    message__sent_at__isnull=False,
)


class FOIRequestSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    protocol = "https"

    def items(self):
        return (
            FOIRequest.objects.filter(_QUALIFYING_MESSAGE, can_publish=True)
            .annotate(
                _last_message_at=Max("message__updated_at", filter=_QUALIFYING_MESSAGE)
            )
            .distinct()
            .order_by("pk")
        )

    def lastmod(self, obj):
        return obj._last_message_at


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return ["index", "faq"]

    def location(self, item):
        return reverse(item)
