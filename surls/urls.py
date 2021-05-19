from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('manage', views.manage, name='manage'),
    url(r'^$', views.launch, name='launch'),
]
