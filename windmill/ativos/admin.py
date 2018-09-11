import csv
from django.contrib import admin
from django.urls import path
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Ativo, Pais, Moeda, Renda_Fixa, Acao
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
