import csv
from django.contrib import admin
from django.urls import path
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from .models import Ativo, Pais, Moeda, Renda_Fixa, Acao, Cambio, Caixa, Fundo_Local, Fundo_Offshore
import ativos.forms
# Register your models here.


admin.site.site_header = "Windmill"
admin.site.site_title = "Portal Windmill"
admin.site.index_title = "Portal Windmill - Anima Investimentos"

class MoedaResource(resources.ModelResource):
    class Meta:
        model = Moeda
        fields = ('id', 'nome', 'codigo')
        export_order = ('id', 'nome', 'codigo')

@admin.register(Moeda)
class MoedaAdmin(ImportExportModelAdmin):
    resource_class = MoedaResource

class PaisResource(resources.ModelResource):
    moeda = fields.Field(
        column_name='moeda',
        attribute='moeda',
        widget=ForeignKeyWidget(Moeda,'codigo')
    )
    class Meta:
        model=Pais
        fields=('id', 'nome', 'moeda')
        export_order=('id', 'nome', 'moeda')

@admin.register(Pais)
class PaisAdmin(ImportExportModelAdmin):
    resource_class=PaisResource

class AcaoResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome'))
    moeda = fields.Field(
        column_name='moeda',
        attribute='moeda',
        widget= ForeignKeyWidget(Moeda, 'codigo')
    )

    class Meta:
        model = Acao
        fields = ('id', 'nome', 'bbg_ticker', 'moeda', 'pais', 'tipo')
        export_order = ('id', 'nome', 'bbg_ticker', 'moeda', 'pais', 'tipo')

@admin.register(Acao)
class AcaoAdmin(ImportExportModelAdmin):
    resource_class = AcaoResource
    list_display = ('nome', 'bbg_ticker', 'moeda', 'tipo')
    list_filter = ('moeda', 'pais', 'tipo')
    search_fields = ('nome', 'bbg_ticker')
    ordering = ('pais', 'nome', 'moeda')

class RendaFixaResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )
    moeda = fields.Field(
        column_name='moeda',
        attribute='moeda',
        widget=ForeignKeyWidget(Moeda, 'codigo')
    )

    class Meta:
        model = Renda_Fixa
        fields = (
            'id',
            'nome',
            'bbg_ticker',
            'moeda',
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
            'moeda_origem',
            'moeda_destino'
        )

@admin.register(Cambio)
class CambioAdmin(ImportExportModelAdmin):
    resource_class = CambioResource
    list_display = ('nome',
        'bbg_ticker',
        'moeda_origem',
        'moeda_destino')
    list_filter = ('moeda_origem', 'moeda_destino')
    search_fields = ('nome', 'bbg_ticker', 'moeda_origem', 'moeda_destino')
    ordering = ('moeda_origem', 'moeda_destino')


class CaixaResource(resources.ModelResource):
    import fundo.models as fm
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome'))
    moeda = fields.Field(
        column_name='moeda',
        attribute='moeda',
        widget=ForeignKeyWidget(Moeda, 'codigo')
    )
    custodia = fields.Field(
        column_name='custodia',
        attribute='custodia',
        widget=ForeignKeyWidget(fm.Custodiante, 'nome')
    )
    corretora = fields.Field(
        column_name='corretora',
        attribute='corretora',
        widget=ForeignKeyWidget(fm.Corretora, 'nome')
    )

    class Meta:
        model = Caixa
        fields = ('id', 'nome', 'moeda', 'corretora', 'custodia')
        export_order = ('id', 'nome', 'moeda', 'corretora', 'custodia')


@admin.register(Caixa)
class CaixaAdmin(ImportExportModelAdmin):
    resource_class = CaixaResource
    list_display = ('id', 'nome', 'moeda', 'custodia', 'corretora')

class FundoLocalResource(resources.ModelResource):
    import fundo.models as fm
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais,'nome')
    )
    moeda = fields.Field(
        column_name='moeda',
        attribute='moeda',
        widget=ForeignKeyWidget(Moeda, 'codigo')
    )
    gestao = fields.Field(
        column_name='Fundo Gerido',
        attribute='gestao',
        widget=ForeignKeyWidget(fm.Fundo, 'nome')
    )

    class Meta:
        model = Fundo_Local
        fields = ('id', 'nome', 'bbg_ticker', 'pais', 'moeda', 'gestao')



@admin.register(Fundo_Local)
class FundoLocalAdmin(ImportExportModelAdmin):
    resource_class=FundoLocalResource
    list_display = ('id', 'nome', 'pais', 'banco', 'agencia', 'conta_corrente' ,'digito')

class FundoOffshoreResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais,'nome')
    )
    moeda = fields.Field(
        column_name='moeda',
        attribute='moeda',
        widget=ForeignKeyWidget(Moeda, 'codigo')
    )

    class Meta:
        model = Fundo_Offshore
        fields = ('nome', 'bbg_ticker', 'pais', 'moeda')

@admin.register(Fundo_Offshore)
class FundoOffshoreAdmin(ImportExportModelAdmin):
    resource_class=FundoOffshoreResource
    list_display = ('id', 'nome', 'pais')
