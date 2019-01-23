from django import forms
from django.contrib import admin
from . import models
import ativos.models
import fundo.models
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.contrib.contenttypes.admin import GenericTabularInline
# Register your models here.
@admin.register(models.Preco)
class PrecoAdmin(ImportExportModelAdmin):
    list_display = ('ativo', 'data_referencia', 'preco_fechamento', \
        'preco_contabil', 'preco_gerencial', 'preco_estimado')

    exclude = ('deletado_em',)
