import csv
from django.contrib import admin
from django.urls import path
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Fundo, Administradora, Gestora, Distribuidora, Corretora, Contato
from ativos.models import Pais
import ativos.forms

# Register your models here.
admin.site.register(Administradora)
admin.site.register(Gestora)
admin.site.register(Distribuidora)
admin.site.register(Corretora)
admin.site.register(Contato)

class FundoResource(resources.ModelResource):
    administradora = fields.Field(
        column_name='administradora',
        attribute='administradora',
        widget=ForeignKeyWidget(Administradora, 'nome')
    )
    gestora = fields.Field(
        column_name='gestora',
        attribute='gestora',
        widget=ForeignKeyWidget(Gestora, 'nome')
    )
    distribuidora = fields.Field(
        column_name='distribuidora',
        attribute='distribuidora',
        widget=ForeignKeyWidget(Distribuidora, 'nome')
    )
    corretora = fields.Field(
        column_name='corretora',
        attribute='corretora',
        widget=ForeignKeyWidget(Corretora, 'nome')
    )
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )

    class Meta:
        model = Fundo
        fields = ('nome', 'administradora', 'gestora', 'distribuidora',
            'categoria', 'data_de_inicio', 'pais', 'taxa_administracao',
            'capitalizacao_taxa_adm')
        export_order = ('nome', 'administradora', 'gestora', 'distribuidora',
            'categoria', 'data_de_inicio', 'pais', 'taxa_administracao',
            'capitalizacao_taxa_adm')

@admin.register(Fundo)
class FundoAdmin(ImportExportModelAdmin):
    resource_class = FundoResource
    list_display = ('nome', 'administradora', 'gestora', 'distribuidora',
        'categoria', 'data_de_inicio', 'pais', 'taxa_administracao',
        'capitalizacao_taxa_adm')
    list_filter = ('administradora', 'gestora', 'pais', 'categoria')
    search_fields = ('nome',)
    ordering = ('pais', 'nome')
