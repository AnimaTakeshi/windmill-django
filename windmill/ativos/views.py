from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import TemplateView

from .models import Acao

def ativos_home(request):
    return HttpResponse('<html><title>Cadastro de ativos</title></html>')

def acoes(request):
    acoes = Acao.objects.all()
    return render(request,
        'acoes/cadastro.html',
        {'acoes':acoes})

class CadastroView(TemplateView):
    template_name = 'acoes/cadastro.html'
