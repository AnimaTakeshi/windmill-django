from django.urls import path, include

from . import views

app_name='ativos'

urlpatterns = [
    path('', views.ativos_home, name='ativos_home'),
    path('acoes/', views.CadastroAcaoView.as_view(), name='cadastro_acao'),
    path('lista-acoes/', views.AcoesView.as_view(), name='lista_acao')
]
