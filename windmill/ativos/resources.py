from django.urls import reverse
from import_export import resources
from .models import Acao

class AcaoResource(resources.ModelResource):
    class Meta:
        model = Acao
