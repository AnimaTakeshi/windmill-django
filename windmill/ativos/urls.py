from django.urls import path, include

from . import views

app_name='ativos'

urlpatterns = [
    path('', views.ativos_home, name='ativos_home'),
    path('acoes/', views.CadastroView.as_view(), name='cadastro')
]
