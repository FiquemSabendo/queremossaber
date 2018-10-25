from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.FOIRequestRedirectView.as_view(), name='foirequest_search'),
    path('new/', views.CreateFOIRequestView.as_view(), name='foi_request_new'),
    path('public_body/new/', views.CreatePublicBodyView.as_view(), name='publicbody_new'),
    re_path(
        r'^(?P<slug>[\w\d]+)/$',
        views.FOIRequestView.as_view(),
        name='foirequest_detail'
    ),
]
