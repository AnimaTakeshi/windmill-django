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
    exclude = ('deletado_em',)

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
    exclude = ('deletado_em',)

    class Meta:
        model = models.BoletaRendaFixaLocal

@admin.register(models.BoletaRendaFixaOffshore)
class BoletaRendaFixaOffAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'data_operacao', 'data_liquidacao', 'corretora',\
        'custodia', 'corretagem', 'fundo', 'operacao', 'quantidade', \
        'nominal', 'taxa', 'preco', 'caixa_alvo')
    exclude = ('deletado_em',)



@admin.register(models.BoletaCPR)
class BoletaCPRAdmin(ImportExportModelAdmin):
    class Meta:
        model = models.BoletaCPR

    list_display = ('descricao', 'fundo', 'valor_cheio', 'valor_parcial', 'data_inicio', 'data_pagamento')
    exclude = ('deletado_em', 'content_type', 'object_id')


@admin.register(models.BoletaProvisao)
class BoletaProvisaoAdmin(ImportExportModelAdmin):
    class Meta:
        model = models.BoletaProvisao

    list_display = ('descricao', 'caixa_alvo', 'fundo', 'data_pagamento', 'financeiro')
    exclude = ('content_type', 'object_id', 'deletado_em')

@admin.register(models.BoletaEmprestimo)
class BoletaEmprestimoAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'data_operacao', 'fundo' ,'data_vencimento', 'data_liquidacao',
        'operacao' ,'quantidade', 'taxa', 'preco', 'financeiro')
    exclude = ('relacao_quantidade', 'relacao_movimentacao', 'deletado_em')

@admin.register(models.BoletaFundoLocal)
class BoletaFundoLocalAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'data_operacao', 'data_cotizacao', 'data_liquidacao',\
        'fundo', 'operacao', 'liquidacao', 'financeiro', 'quantidade', \
        'preco', 'caixa_alvo', 'custodia')

    exclude = ('deletado_em',)

    class Meta:
        model = models.BoletaFundoLocal

@admin.register(models.BoletaFundoOffshore)
class BoletaFundoOffAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'estado', 'data_operacao', 'data_cotizacao',\
        'data_liquidacao', 'fundo', 'financeiro', 'preco', 'quantidade',
        'operacao', 'caixa_alvo', 'custodia')

    exclude = ('deletado_em',)

@admin.register(models.BoletaPassivo)
class BoletaPassivoAdmin(ImportExportModelAdmin):
    list_display = ('cotista', 'valor' ,'data_operacao', 'data_cotizacao', \
        'data_liquidacao' ,'operacao', 'fundo', 'cota', )
    exclude = ('certificado_passivo' ,'content_type', 'object_id', 'deletado_em')

@admin.register(models.BoletaCambio)
class BoletaCambioAdmin(ImportExportModelAdmin):
    list_display = ('fundo', 'caixa_origem', 'caixa_destino', 'data_operacao', \
        'cambio', 'taxa', 'financeiro_origem', 'financeiro_final', \
        'data_liquidacao_origem', 'data_liquidacao_destino')
    exclude = ('deletado_em',)
