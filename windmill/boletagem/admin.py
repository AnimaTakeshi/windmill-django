import csv
from django.contrib import admin
from django import forms
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import BoletaAcao, BoletaCPR
from ativos.models import Acao
from .forms import FormBoletaAcao
from boletagem.forms import FormBoletaAcao
# Register your models here.

@admin.register(BoletaAcao)
class BoletaAcaoAdmin(ImportExportModelAdmin):
    form = FormBoletaAcao
    acao = fields.Field(
        column_name='ativos.acao',
        attribute='ativos.acao',
        widget=ForeignKeyWidget(Acao, 'nome')
    )

    class Meta:
        model = BoletaAcao

@admin.register(BoletaCPR)
class  BoletaCPRAdmin(ImportExportModelAdmin):
    class Meta:
        model = BoletaCPR
