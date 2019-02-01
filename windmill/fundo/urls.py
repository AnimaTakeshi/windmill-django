from django.urls import path, include
from django.views.generic import TemplateView

from . import views

app_name='fundos'

urlpatterns = [
    path('base/', TemplateView.as_view(template_name='base.html'), name='base'),
    path('base_site/', TemplateView.as_view(template_name='base_site.html'), name='base_site'),
    # path('acoes/cadastro', views.CadastroAcaoView.as_view(), name='cadastro_acao'),
    # path('acoes/', views.AcoesView.as_view(), name='lista_acao'),
    # path('acoes/<int:pk>/', views.AcaoDetalheView.as_view(), name='detalhe_acao'),
    # path('acoes/<int:pk>/editar', views.AcaoEditarView.as_view(), name='editar_acao'),
    # path('acoes/upload_csv', views.UploadCSVAcaoView.as_view(), name='upload_csv_acao'),
]
