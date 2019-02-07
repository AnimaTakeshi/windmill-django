from django.contrib import admin
from .models import Feriado, Estado, Cidade, Calendario
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from ativos.models import Pais

# Register your models here.
class FeriadoResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )

    estado = fields.Field(
        column_name='estado',
        attribute='estado',
        widget=ForeignKeyWidget(Estado, 'nome')
    )

    cidade = fields.Field(
        column_name='cidade',
        attribute='cidade',
        widget=ForeignKeyWidget(Cidade, 'nome')
    )

    class Meta:
        model = Feriado
        fields = ('pais', 'cidade', 'estado', 'data', 'id')
        export_order = ('pais', 'cidade', 'estado', 'data', 'id')

@admin.register(Feriado)
class FeriadoAdmin(ImportExportModelAdmin):
    resource_class = FeriadoResource
    list_display = ('data', 'pais', 'estado', 'cidade')

class EstadoResource(resources.ModelResource):
    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )
    class Meta:
        model = Estado
        fields = ('nome', 'pais')

@admin.register(Estado)
class EstadoAdmin(ImportExportModelAdmin):
    resource_class= EstadoResource
    list_display = ('nome', 'pais')

class CidadeResource(resources.ModelResource):
    nome = fields.Field(
        column_name = 'nome',
        attribute = 'nome',
    )

    estado = fields.Field(
        column_name='estado',
        attribute='estado',
        widget=ForeignKeyWidget(Estado, 'nome')
    )

    class Meta:
        models = Cidade
        fields = ('nome', 'estado')

@admin.register(Cidade)
class CidadeAdmin(ImportExportModelAdmin):
    resource_class = CidadeResource

class CalendarioResource(resources.ModelResource):
    nome = fields.Field(
        column_name='nome',
        attribute='nome',
    )

    pais = fields.Field(
        column_name='pais',
        attribute='pais',
        widget=ForeignKeyWidget(Pais, 'nome')
    )
    estado = fields.Field(
        column_name='estado',
        attribute='estado',
        widget=ForeignKeyWidget(Estado, 'nome')
    )
    cidade = fields.Field(
        column_name='cidade',
        attribute='cidade',
        widget=ForeignKeyWidget(Cidade, 'nome')
    )

@admin.register(Calendario)
class CalendarioAdmin(ImportExportModelAdmin):
    resource_class = CalendarioResource
    list_display = ('id', 'nome', 'pais', 'estado', 'cidade')
