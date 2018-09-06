from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .models import Acao

def ativos_home(request):
    return HttpResponse('<html><title>Cadastro de ativos</title></html>')

def acoes(request):
    acoes = Acao.objects.all()
    return render(request,
        'acoes/cadastro.html',
        {'acoes':acoes})

class CadastroAcaoView(CreateView):
    model = Acao
    template_name = 'acoes/cadastro.html'
    fields = '__all__'

class AcoesView(ListView):
    model = Acao
    template_name ='acoes/lista.html'

class AcaoEditarView(UpdateView):
    model = Acao
    template_name = 'acoes/editar.html'
    fields = "__all__"

class AcaoDetalheView(DetailView):
    model = Acao
    template_name = 'acoes/detalhe.html'
