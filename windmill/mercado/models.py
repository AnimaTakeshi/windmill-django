"""
Este app é voltado para armazenar informações de mercado.
Responsabilidades deste app:
    - Armazenar informações de mercado como:
        Preços
        Proventos
        Volatilidade
        Etc...
    - Os preços armazenados são históricos, ou seja, não são reajustados de
    acordo com proventos anunciados, como dividendos, split, etc.
    - Este app usa o app Ativos como base para nomes de ativos.
"""
import datetime
import decimal
from django.db import models
from django.utils import timezone
import ativos.models as am

class BaseModelQuerySet(models.query.QuerySet):
    def delete(self):
        return super(BaseModelQuerySet, self).update(deletado_em=timezone.now())

    def hard_delete(self):
        return super(BaseModelQuerySet, self).delete()

    def alive(self):
        return self.filter(deletado_em=None)

    def dead(self):
        return self.exclude(deletado_em=None)

class BaseModelManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(BaseModelManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return BaseModelQuerySet(self.model).filter(deletado_em=None)
        return BaseModelQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class BaseModel(models.Model):
    """
    Classe base para criar campos comuns a todas as classes, como 'criado em'
    ou 'atualizado em'
    """
    deletado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = BaseModelManager()
    all_objects = BaseModelManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deletado_em = timezone.now()
        self.save()

    def hard_delete(self):
        super(BaseModel, self).delete()

class Preco(BaseModel):
    """
    Armazena os preços históricos dos ativos.
    """
    ativo = models.ForeignKey('ativos.Ativo', on_delete=models.PROTECT)
    data_referencia = models.DateField()

    # Último preço em que o ativo foi negociado no dia. No caso de derivativos,
    # é o valor do ajuste diário do final do dia. No caso de fundos de ações,
    # é o valor da cota calculada pelo administrador no dia. No caso de fundos
    # negociados na bolsa, como fundos imobiliários, é o valor de fechamendo.
    preco_fechamento = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    # Preço contábil da cota do ativo. No caso de fundos imobiliários, é essa
    # a cota calculada pelo administrador.
    preco_contabil = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    # Preço gerencial de um ativo. Informado pelo gestor do fundo.
    preco_gerencial = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    # Estimativa'
    preco_estimado = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)

    class Meta:
        unique_together = (('ativo', 'data_referencia'),)
