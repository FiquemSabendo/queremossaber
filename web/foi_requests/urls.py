from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from . import views


ONE_DAY = 60 * 60 * 24

urlpatterns = [
    path("", views.FOIRequestRedirectView.as_view(), name="foirequest_search"),
    path(
        "new/",
        cache_page(ONE_DAY)(views.CreateFOIRequestView.as_view()),
        name="foi_request_new",
    ),
    path(
        "public_body/new/",
        cache_page(ONE_DAY)(views.CreatePublicBodyView.as_view()),
        name="publicbody_new",
    ),
    re_path(
        r"^(?P<slug>[\w\d]+)/$",
        views.FOIRequestView.as_view(),
        name="foirequest_detail",
    ),
]
