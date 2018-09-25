import csv
from django.contrib import admin
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.contrib.contenttypes.admin import GenericTabularInline
from . import models
import ativos.models
from . import forms
# Register your models here.

@admin.register(models.BoletaAcao)
class BoletaAcaoAdmin(ImportExportModelAdmin):
    form = forms.FormBoletaAcao
    acao = fields.Field(
        column_name='ativos.acao',
        attribute='ativos.acao',
        widget=ForeignKeyWidget(ativos.models.Acao, 'nome')
    )

    list_display = ('acao', 'data_operacao', 'data_liquidacao', 'corretora',
        'fundo', 'operacao', 'quantidade', 'preco', 'caixa_alvo')
    ordering = ('acao', 'fundo')

    actions = ['fechar_boleta']

    def fechar_boleta(self, request, queryset):
        for boleta in queryset:
            boleta.fechar_boleta()

    fechar_boleta.short_description = "Fechar boleta"

@admin.register(models.BoletaRendaFixaLocal)
class BoletaRendaFixaLocalAdmin(ImportExportModelAdmin):
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
