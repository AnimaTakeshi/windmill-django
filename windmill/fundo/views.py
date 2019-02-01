from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.template import Context
from django.contrib.auth.decorators import login_required

from .models import Fundo

# Create your views here.
def home(request):
    return HttpResponse('Controladoria Anima')

class HomePageView(ListView):
    model = Fundo
    template_name='base_site.html'
