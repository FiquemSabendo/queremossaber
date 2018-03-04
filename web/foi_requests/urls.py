from django.urls import path, re_path

from . import views

urlpatterns = [
    path('new/', views.CreateMessageView.as_view(), name='message_new'),
    re_path(
        '^(?P<slug>[\w\d]+)/$',
        views.FOIRequestView.as_view(),
        name='foirequest_detail'
    ),
]
