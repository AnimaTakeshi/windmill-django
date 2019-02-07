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
    custodia = fields.Field(
        column_name='custodia',
        attribute='custodia',
        widget=ForeignKeyWidget(fundo.models.Custodiante, 'nome')
    )
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )
    caixa_alvo = fields.Field(
        column_name='caixa_alvo',
        attribute='caixa_alvo',
        widget=ForeignKeyWidget(ativos.models.Caixa, 'nome')
    )

    class Meta:
        model = models.BoletaAcao
        fields = ('id', 'acao', 'data_operacao' ,'data_liquidacao', 'corretora',
            'custodia', 'fundo', 'operacao', 'quantidade', 'preco', 'caixa_alvo')
        export_order = ('acao', 'data_operacao' ,'data_liquidacao', 'corretora',
            'custodia', 'fundo', 'operacao', 'quantidade', 'preco')

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

class BoletaCPRResource(resources.ModelResource):

    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )

    class Meta:
        model = models.BoletaCPR
        fields = ('id', 'descricao', 'fundo', 'valor_parcial', 'valor_cheio',
            'data_inicio', 'data_vigencia_inicio', 'data_vigencia_fim',
            'data_pagamento', 'tipo', 'capitalizacao')
        export_order = ('id', 'descricao', 'fundo', 'valor_parcial', 'valor_cheio',
            'data_inicio', 'data_vigencia_inicio', 'data_vigencia_fim',
            'data_pagamento', 'tipo', 'capitalizacao')

@admin.register(models.BoletaCPR)
class BoletaCPRAdmin(ImportExportModelAdmin):
    class Meta:
        model = models.BoletaCPR
    resource_class = BoletaCPRResource
    list_display = ('id','descricao', 'fundo', 'valor_cheio',
        'valor_parcial', 'data_inicio', 'data_pagamento', 'content_object')
    exclude = ('deletado_em', 'content_type', 'object_id')

class BoletaProvisaoResource(resources.ModelResource):
    caixa_alvo = fields.Field(
        column_name='caixa_alvo',
        attribute='caixa_alvo',
        widget=ForeignKeyWidget(ativos.models.Caixa, 'nome')
    )
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )

    class Meta:
        model = models.BoletaProvisao
        fields = ('id', 'descricao', 'caixa_alvo', 'fundo', 'data_pagamento',
            'financeiro', 'estado')

@admin.register(models.BoletaProvisao)
class BoletaProvisaoAdmin(ImportExportModelAdmin):
    resource_class = BoletaProvisaoResource
    list_display = ('descricao', 'caixa_alvo', 'fundo', 'data_pagamento', 'financeiro')
    exclude = ('deletado_em', )

@admin.register(models.BoletaEmprestimo)
class BoletaEmprestimoAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'data_operacao', 'fundo' ,'data_vencimento', 'data_liquidacao',
        'operacao' ,'quantidade', 'taxa', 'preco', 'financeiro')
    exclude = ('relacao_quantidade', 'relacao_movimentacao', 'deletado_em')

class BoletaFundoLocalResource(resources.ModelResource):
    ativo = fields.Field(
        column_name='ativo',
        attribute='ativo',
        widget=ForeignKeyWidget(ativos.models.Fundo_Local, 'nome')
    )
    custodia = fields.Field(
        column_name='custodia',
        attribute='custodia',
        widget=ForeignKeyWidget(fundo.models.Custodiante, 'nome')
    )
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )
    caixa_alvo = fields.Field(
        column_name='caixa_alvo',
        attribute='caixa_alvo',
        widget=ForeignKeyWidget(ativos.models.Caixa, 'nome')
    )

    class Meta:
        model = models.BoletaFundoLocal
        fields = ('id', 'ativo', 'data_operacao', 'data_cotizacao', \
            'data_liquidacao', 'fundo', 'operacao', 'liquidacao',\
            'financeiro', 'quantidade', 'preco', 'caixa_alvo', 'custodia')
        export_order = ('id', 'ativo', 'data_operacao', 'data_cotizacao', \
            'data_liquidacao', 'fundo', 'operacao', 'liquidacao',\
            'financeiro', 'quantidade', 'preco', 'caixa_alvo', 'custodia')

@admin.register(models.BoletaFundoLocal)
class BoletaFundoLocalAdmin(ImportExportModelAdmin):
    resource_class = BoletaFundoLocalResource
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

class BoletaPassivoResource(resources.ModelResource):
    cotista = fields.Field(
        column_name='cotista',
        attribute='cotista',
        widget=ForeignKeyWidget(fundo.models.Cotista, 'nome')
    )
    fundo = fields.Field(
        column_name='fundo',
        attribute='fundo',
        widget=ForeignKeyWidget(fundo.models.Fundo, 'nome')
    )

    class Meta:
        model = models.BoletaPassivo
        fields = ('id', 'cotista', 'valor', 'data_operacao', 'data_cotizacao',\
        'data_liquidacao', 'operacao', 'fundo', 'cota')
        export_order = ('id', 'cotista', 'valor', 'data_operacao', 'data_cotizacao',\
        'data_liquidacao', 'operacao', 'fundo', 'cota')


@admin.register(models.BoletaPassivo)
class BoletaPassivoAdmin(ImportExportModelAdmin):
    resource_class = BoletaPassivoResource
    list_display = ('cotista', 'valor' ,'data_operacao', 'data_cotizacao', \
        'data_liquidacao' ,'operacao', 'fundo', 'cota', )
    exclude = ('certificado_passivo' ,'content_type', 'object_id', 'deletado_em')

@admin.register(models.BoletaCambio)
class BoletaCambioAdmin(ImportExportModelAdmin):
    list_display = ('fundo', 'caixa_origem', 'caixa_destino', 'data_operacao', \
        'cambio', 'taxa', 'financeiro_origem', 'financeiro_final', \
        'data_liquidacao_origem', 'data_liquidacao_destino')
    exclude = ('deletado_em',)
