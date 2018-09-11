import csv
from django.contrib import admin
from django.urls import path
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Ativo, Pais, Moeda, Renda_Fixa, Acao, Cambio
# Register your models here.

admin.site.register(Pais)
admin.site.register(Moeda)
admin.site.site_header = "Windmill"
admin.site.site_title = "Portal Windmill"
admin.site.index_title = "Portal Windmill - Anima Investimentos"

class AcaoResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome'))

    class Meta:
        model = Acao
        fields = ('nome', 'bbg_ticker', 'pais', 'tipo', 'id')
        export_order = ('id', 'nome', 'bbg_ticker', 'pais', 'tipo')

@admin.register(Acao)
class AcaoAdmin(ImportExportModelAdmin):
    resource_class = AcaoResource
    list_display = ('nome', 'bbg_ticker', 'pais', 'tipo')
    list_filter = ('pais', 'tipo')
    search_fields = ('nome', 'bbg_ticker')
    ordering = ('pais', 'nome')


class RendaFixaResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )

    class Meta:
        model = Renda_Fixa
        fields = (
            'id',
            'nome',
            'bbg_ticker',
            'pais',
            'vencimento',
            'cupom',
            'info',
            'periodo'
        )

@admin.register(Renda_Fixa)
class RendaFixaAdmin(ImportExportModelAdmin):
    resource_class = RendaFixaResource
    list_display = ('nome',
        'bbg_ticker',
        'pais',
        'vencimento',
        'cupom',
        'info',
        'periodo')
    list_filter = ('pais', 'vencimento')
    search_fields = ('nome', 'bbg_ticker')
    ordering = ('pais', 'vencimento', 'nome')

class CambioResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )
    moeda_origem = fields.Field(
        column_name='moeda_origem',
        attribute='moeda_origem',
        widget=ForeignKeyWidget(Moeda, 'codigo')
    )
    moeda_destino = fields.Field(
        column_name='moeda_destino',
        attribute='moeda_destino',
        widget=ForeignKeyWidget(Moeda, 'codigo')
    )

    class Meta:
        model = Cambio
        fields = (
            'id',
            'nome',
            'bbg_ticker',
            'pais',
            'moeda_origem',
            'moeda_destino'
        )

@admin.register(Cambio)
class CambioAdmin(ImportExportModelAdmin):
    resource_class = CambioResource
    list_display = ('nome',
        'bbg_ticker',
        'pais',
        'moeda_origem',
        'moeda_destino')
    list_filter = ('pais', 'moeda_origem', 'moeda_destino')
    search_fields = ('nome', 'bbg_ticker', 'moeda_origem', 'moeda_destino')
    ordering = ('pais', 'moeda_origem', 'moeda_destino')

class AtivoResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )

    class Meta:
        model = Ativo
        fields = (
            'id',
            'nome',
            'bbg_ticker',
            'pais'
        )

class CambioInLine(admin.StackedInline):
    model = Cambio

@admin.register(Ativo)
class AtivoAdmin(ImportExportModelAdmin):
    resource_class = AtivoResource
    list_display = ('nome',
        'bbg_ticker',
        'pais')
    list_filter = ('pais',)
    search_fields = ('nome', 'bbg_ticker')
    ordering = ('pais',)
    inlines = [CambioInLine]
