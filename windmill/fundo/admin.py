import csv
from django.contrib import admin
from django.urls import path
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import Fundo, Administradora, Gestora, Custodiante, Corretora, Contato, Carteira, Vertice, Cotista
import ativos.models as am
import ativos.forms

# Register your models here.
admin.site.register(Gestora)
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
    corretora = fields.Field(
        column_name='corretora',
        attribute='corretora',
        widget=ForeignKeyWidget(Corretora, 'nome')
    )
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(am.Pais, 'nome')
    )
    caixa_padrao = fields.Field(
        column_name='caixa_padrao',
        attribute='caixa_padrao',
        widget=ForeignKeyWidget(am.Caixa, 'nome')
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
    exclude = ('deletado_em' ,)

class ContatoInLine(GenericTabularInline):
    model = Contato

@admin.register(Administradora)
class AdministradoraAdmin(ImportExportModelAdmin):
    inlines = [
        ContatoInLine,
    ]

@admin.register(Corretora)
class CorretoraAdmin(ImportExportModelAdmin):
    list_display = ('id', 'nome')

@admin.register(Custodiante)
class CustodianteAdmin(ImportExportModelAdmin):
    list_display = ('id', 'nome')

@admin.register(Cotista)
class CotistaAdmin(ImportExportModelAdmin):
    list_display = ('nome', 'n_doc', 'fundo_cotista')
    exclude = ('deletado_em' ,)

class VerticeResource(resources.ModelResource):
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(Fundo, 'nome')
    )
    custodia = fields.Field(
        column_name='custodia',
        attribute='custodia',
        widget=ForeignKeyWidget(Custodiante, 'nome')
    )
    corretora = fields.Field(
        column_name='corretora',
        attribute='corretora',
        widget=ForeignKeyWidget(Corretora, 'nome')
    )

    class Meta:
        model = Vertice
        fields = ('id', 'fundo', 'custodia', 'corretora', 'quantidade', 'valor',
            'preco', 'data_preco', 'movimentacao', 'data', 'cambio')
        export_order = ('fundo', 'custodia', 'corretora', 'quantidade', 'valor',
            'preco', 'data_preco', 'movimentacao', 'data', 'cambio')

@admin.register(Vertice)
class VerticeAdmin(ImportExportModelAdmin):
    resource_class = VerticeResource
    list_display = ('id', 'fundo', 'custodia', 'corretora', 'quantidade', 'valor',
        'preco', 'data_preco', 'movimentacao', 'data', 'cambio', 'content_object')
    exclude = ('deletado_em',)

class CarteiraResource(resources.ModelResource):
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(Fundo, 'nome')
    )

    class Meta:
        model = Carteira
        fields = ('id', 'fundo', 'vertices', 'data', 'cota', 'pl', 'movimentacao')
        export_order = ('id', 'fundo', 'vertices', 'data', 'cota', 'pl', 'movimentacao')

@admin.register(Carteira)
class CarteiraAdmin(ImportExportModelAdmin):
    resource_class = CarteiraResource
    list_display = ('id', 'fundo', 'data', 'cota', 'pl', 'movimentacao')
    exclude = ('deletado_em',)
