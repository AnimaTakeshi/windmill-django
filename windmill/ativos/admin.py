from django.contrib import admin
from .models import Ativo, Pais, Moeda, Renda_Fixa, Acao
# Register your models here.

admin.site.register(Pais)
admin.site.register(Moeda)
admin.site.register(Renda_Fixa)
admin.site.register(Acao)
