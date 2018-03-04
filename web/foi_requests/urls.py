from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('p/new/', views.CreateMessageView.as_view(), name='message_new'),
    re_path(
        '^p/(?P<slug>[\w\d]+)/$',
        views.FOIRequestView.as_view(),
        name='foirequest_detail'
    ),
]
