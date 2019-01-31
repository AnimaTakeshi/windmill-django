from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView

# Create your views here.
def fundo_home(request):
    return HttpResponse('Controladoria Anima')

class HomePageView(TemplateView):
    template_name='base.html'
