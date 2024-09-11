from django.urls import path

from . import views

urlpatterns = [
    path("", views.WhoamiView.as_view(), name="whoami_get"),
]
