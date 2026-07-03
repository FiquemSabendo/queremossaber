from django.urls import path

from . import views


urlpatterns = [
    path(
        "foi_requests/",
        views.CreateFOIRequestApiView.as_view(),
        name="api_foi_request_create",
    ),
    path(
        "public_bodies/",
        views.PublicBodySearchApiView.as_view(),
        name="api_public_body_search",
    ),
]
