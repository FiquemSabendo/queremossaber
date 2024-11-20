"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.views.generic import TemplateView
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.views.static import serve
from django.views.decorators.cache import cache_page


ONE_DAY = 60 * 60 * 24

urlpatterns = [
    path(
        "",
        cache_page(ONE_DAY)(TemplateView.as_view(template_name="index.html")),
        name="index",
    ),
    path(
        "faq/",
        cache_page(ONE_DAY)(TemplateView.as_view(template_name="faq.html")),
        name="faq",
    ),
    path("p/", include("web.foi_requests.urls")),
    path("whoami/", include("web.whoami.urls")),
    path("a/", admin.site.urls),
]

if not settings.ENABLE_S3:
    urlpatterns = [
        re_path(
            r"^upload/(?P<path>.*)$",
            serve,
            {
                "document_root": settings.MEDIA_ROOT,
                "show_indexes": False,
            },
        )
    ] + urlpatterns

if settings.DEBUG:
    import debug_toolbar.toolbar

    urlpatterns += debug_toolbar.toolbar.debug_toolbar_urls()
