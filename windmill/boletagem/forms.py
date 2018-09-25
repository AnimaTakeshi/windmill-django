from django import forms
from . import models

class FormBoletaAcao(forms.ModelForm):

    class Meta:
        model = models.BoletaAcao
        fields = "__all__"

    def clean_quantidade(self):
        data = self.cleaned_data['quantidade']
        print(data)
        if self.cleaned_data['operacao'] == 'C':
            data = abs(data)
        else:
            data = -abs(data)
        return data

class FormBoletaRendaFixaLocal(forms.ModelForm):

    class Meta:
        model = models.BoletaRendaFixaLocal
        fields = "__all__"

    def clean_quantidade(self):
        data = self.cleaned_data['quantidade']
        print(data)
        if self.cleaned_data['operacao'] == 'C':
            data = abs(data)
        else:
            data = -abs(data)
        return data
