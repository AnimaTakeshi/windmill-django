from django.forms import ModelForm
from django import forms
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.contrib import admin
from .models import Acao, Pais, Moeda


class AcaoForm(ModelForm):
    pais = forms.ModelChoiceField(queryset=Pais.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(AcaoForm, self).__init__(*args, **kwargs)
        add_related_field_wrapper(self, 'pais')

    class Meta:
        model = Acao
        fields = "__all__"

class AcaoCSVForm(forms.Form):
    file = forms.FileField()

def add_related_field_wrapper(form, col_name):
    rel_model = form.Meta.model
    rel = rel_model._meta.get_field(col_name).rel
    form.fields[col_name].widget = RelatedFieldWidgetWrapper(
    form.fields[col_name].widget, rel, admin.site, can_add_related=True,
    can_change_related=False)
