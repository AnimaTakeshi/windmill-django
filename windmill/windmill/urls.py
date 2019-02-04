"""windmill URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views as home_views
from fundo import views as fundo_views
from ativos import views as ativos_views

urlpatterns = [
    path('', home_views.custom_login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('home/', fundo_views.HomePageView.as_view(), name='home'),
    path('home/processos/', include('fundo.urls', namespace='fundos')),
    path('admin/', admin.site.urls, name='cadastro'),
    path('ativos/', include('ativos.urls', namespace='ativos')),
]
