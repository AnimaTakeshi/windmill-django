from django.urls import path

from . import views

app_name='ativos'

urlpatterns = [
    path('', views.ativos_home, name='ativos_home'),
    path('acoes/', views.acoes, name='acoes')
]
