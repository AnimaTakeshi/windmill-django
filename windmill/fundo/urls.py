from django.urls import path, include
from django.views.generic import TemplateView

from . import views

app_name='fundos'

urlpatterns = [
    path('fechamento/', views.fechamento, name='fechamento'),
    path('base_site/', TemplateView.as_view(template_name='base_site.html'), name='base_site'),
]
