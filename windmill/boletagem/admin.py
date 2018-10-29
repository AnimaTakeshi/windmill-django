import csv
from django.contrib import admin
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.contrib.contenttypes.admin import GenericTabularInline
from . import models
import ativos.models
import fundo.models
from . import forms
# Register your models here.

class BoletaAcaoResource(resources.ModelResource):
    acao = fields.Field(
        column_name='acao',
        attribute='acao',
        widget=ForeignKeyWidget(ativos.models.Acao, 'nome')
    )
    corretora = fields.Field(
        column_name='corretora',
        attribute='corretora',
        widget=ForeignKeyWidget(fundo.models.Corretora, 'nome')
    )
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )

    class Meta:
        model = models.BoletaAcao
        fields = ('acao', 'data_operacao' ,'data_liquidacao', 'corretora',
            'fundo', 'operacao', 'quantidade', 'preco', 'caixa_alvo')
        export_order = ('acao', 'data_operacao' ,'data_liquidacao', 'corretora',
            'fundo', 'operacao', 'quantidade', 'preco')

@admin.register(models.BoletaAcao)
class BoletaAcaoAdmin(ImportExportModelAdmin):
    resource_class = BoletaAcaoResource
    form = forms.FormBoletaAcao

    list_display = ('acao', 'data_operacao', 'data_liquidacao', 'corretora',
        'fundo', 'operacao', 'quantidade', 'preco', 'caixa_alvo', )

    ordering = ('acao', 'fundo')

    actions = ['fechar_boleta']

    def fechar_boleta(self, request, queryset):
        for boleta in queryset:
            boleta.fechar_boleta()

    fechar_boleta.short_description = "Fechar boleta"

class BoletaRendaFixaLocalResource(resources.ModelResource):
    acao = fields.Field(
        column_name='ativo',
        attribute='ativo',
        widget=ForeignKeyWidget(ativos.models.Renda_Fixa, 'nome')
    )
    corretora = fields.Field(
        column_name='corretora',
        attribute='corretora',
        widget=ForeignKeyWidget(fundo.models.Corretora, 'nome')
    )
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )

    class Meta:
        model = models.BoletaRendaFixaLocal
        fields = ('ativo', 'data_operacao' ,'data_liquidacao', 'corretora',
            'fundo', 'operacao', 'quantidade', 'preco', 'taxa', 'caixa_alvo')
        export_order = ('acao', 'data_operacao' ,'data_liquidacao', 'corretora',
            'fundo', 'operacao', 'quantidade', 'preco', 'taxa')


@admin.register(models.BoletaRendaFixaLocal)
class BoletaRendaFixaLocalAdmin(ImportExportModelAdmin):
    resource_class = BoletaRendaFixaLocalResource
    form = forms.FormBoletaRendaFixaLocal
    ativo = fields.Field(
        column_name='ativos.renda_fixa',
        attribute='ativos.renda_fixa',
        widget=ForeignKeyWidget(ativos.models.Renda_Fixa, 'nome')
    )
    list_display = ('ativo', 'data_operacao', 'data_liquidacao', 'corretora',
        'fundo', 'operacao', 'quantidade', 'preco', 'caixa_alvo')

    class Meta:
        model = models.BoletaRendaFixaLocal

@admin.register(models.BoletaCPR)
class BoletaCPRAdmin(ImportExportModelAdmin):
    class Meta:
        model = models.BoletaCPR

    list_display = ('descricao', 'fundo', 'valor_cheio', 'valor_parcial', 'data_inicio', 'data_pagamento')

@admin.register(models.BoletaProvisao)
class BoletaProvisaoAdmin(ImportExportModelAdmin):
    class Meta:
        model = models.BoletaProvisao

    list_display = ('descricao', 'caixa_alvo', 'fundo', 'data_pagamento', 'financeiro')

@admin.register(models.BoletaEmprestimo)
class BoletaEmprestimoAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'data_operacao', 'fundo' ,'data_vencimento', 'data_liquidacao',
        'operacao' ,'quantidade', 'taxa', 'preco', 'financeiro')
    exclude = ('relacao_quantidade', 'relacao_movimentacao')
