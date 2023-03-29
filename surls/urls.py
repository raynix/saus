from django.urls import re_path
from django.urls import path

from . import views

urlpatterns = [
    path('manage', views.manage, name='manage'),
    re_path(r'^$', views.launch, name='launch'),
    path('qr.png', views.qr, name='qr'),
]
