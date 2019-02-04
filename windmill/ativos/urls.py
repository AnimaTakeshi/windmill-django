from django.urls import path, include

from . import views

app_name='ativos'

urlpatterns = [
    #path('', views.ativos_home, name='ativos_home'),
    path('acoes/cadastro', views.AcaoCreateView.as_view(), name='cadastro_acao'),
    path('acoes/', views.AcoesView.as_view(), name='lista_acao'),
    path('acoes/<int:pk>/', views.AcaoDetalheView.as_view(), name='detalhe_acao'),
    path('acoes/<int:pk>/editar', views.AcaoEditarView.as_view(), name='editar_acao'),
    path('acoes/upload_csv', views.UploadCSVAcaoView.as_view(), name='upload_csv_acao'),
]
