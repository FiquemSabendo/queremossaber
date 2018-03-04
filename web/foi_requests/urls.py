from django.urls import path

from . import views

urlpatterns = [
    path(r'^$', views.IndexView.as_view(), name='index'),
    path(r'^p/new$', views.CreateMessageView.as_view(), name='message_new'),
]
