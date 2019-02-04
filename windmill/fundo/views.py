from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.template import Context
from django.contrib.auth.decorators import login_required

from .models import Fundo, Gestora

# Create your views here.

class HomePageView(ListView):
    model = Fundo
    template_name='base_site.html'

def fechamento(request):
    try:
        anima = Gestora.objects.get(anima=True)
        fundos = Fundo.objects.filter(gestora=anima)
    except:
        fundos = Fundo.objects.none()
    return render(request, 'fechamento.html', {'fundos': fundos})
