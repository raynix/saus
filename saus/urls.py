"""saus URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.urls import include, re_path

from surls import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
    path('bookmarks/', views.bookmark_list, name='bookmark_list'),
    path('bookmarks/create/', views.bookmark_create, name='bookmark_create'),
    path('bookmarks/<int:bookmark_id>/edit/', views.bookmark_edit, name='bookmark_edit'),
    path('bookmarks/<int:bookmark_id>/delete/', views.bookmark_delete, name='bookmark_delete'),
    path('bookmarks/<int:bookmark_id>/visit/', views.bookmark_visit, name='bookmark_visit'),
    path('', views.shorten, name='shorten'),
    re_path(r'^(?P<keyword>[0-9a-zA-Z_]+)/?', include('surls.urls')),
]
