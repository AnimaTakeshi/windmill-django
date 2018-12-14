"""
Modelos deste app servem para armazenar informações que são constantes
sobre ativos financeiros. Informações de mercado, como preço, volatilidade,
etc... serão armazenados no app Mercado.
Responsabilidades deste app:
    - Armazenamento de informações estáticas sobre ativos do mercado.
"""

import datetime
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation
import fundo.models

# Create your models here.

class Moeda(models.Model):
    nome = models.CharField(max_length=15, unique=True)
    codigo = models.CharField(max_length=3, unique=True)

    class Meta:
        verbose_name_plural = 'Moedas'

    def __str__(self):
        return '%s' % (self.codigo)

class Pais(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    moeda = models.ForeignKey(Moeda, on_delete=models.PROTECT)

    def __str__(self):
        return '%s' % (self.nome)

    class Meta:
        verbose_name_plural = 'Países'

class Ativo(models.Model):

    nome = models.CharField(max_length=25, unique=True)
    bbg_ticker = models.CharField(max_length=25, unique=True, null=True, blank=True, default=None)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, null=True, blank=True)
    # Moeda que representa a apresentação final do ativoself.
    moeda = models.ForeignKey(Moeda, on_delete=models.PROTECT, null=True, blank=True)
    isin = models.CharField(max_length=25, unique=True, null=True, blank=True)
    vertice = GenericRelation('fundo.Vertice')
    descricao = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Ativos'

    def __str__(self):
        return '%s' % (self.nome)

    def save(self, *args, **kwargs):
        if self.bbg_ticker == '':
            self.bbg_ticker = None
        super(Ativo, self).save(*args, **kwargs)

class Renda_Fixa(Ativo):
    TIPO_INFO_CHOICES = (
        ("PU", "PU"),
        ("Yield", "Yield")
    )
    vencimento = models.DateField(default=datetime.date.max)
    cupom = models.DecimalField(max_digits=7, decimal_places=5, null=True,
        default=0)
    info = models.CharField("informação de mercado", max_length=5,
        choices=TIPO_INFO_CHOICES, default="PU")
    periodo = models.IntegerField("periodicidade do cupom em meses", default=0)

    class Meta:
        verbose_name_plural = 'Ativos de Renda Fixa'

class Acao(Ativo):
    TIPO_CHOICES=(
        ("PN", "PN"),
        ("ON", "ON")
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=True)

    class Meta:
        verbose_name_plural = 'Ações'

    def get_absolute_url(self):
        return reverse('ativos:detalhe_acao', args=[str(self.id)])

class Cambio(Ativo):
    """
    Não é um ativo em si, mas como possui valor (taxa de conversão entre
    moedas), decidimos caracterizá-lo como tal para facilitar.
    """

    moeda_origem = models.ForeignKey(Moeda, on_delete=models.PROTECT,
        null=False, blank=False, related_name='cambio_moeda_origem')
    moeda_destino = models.ForeignKey(Moeda, on_delete=models.PROTECT,
        null=False, blank=False, related_name='cambio_moeda_destino')

    class Meta:
        verbose_name_plural = 'Câmbios'

class Caixa(Ativo):

    # Indica a moeda do caixa
    zeragem = models.ForeignKey(Ativo, blank=True, null=True,
        on_delete=models.PROTECT, default=None, related_name='caixas')
    custodia = models.ForeignKey('fundo.Custodiante', on_delete=models.PROTECT)
    corretora = models.ForeignKey('fundo.Corretora', on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Caixas"

class Fundo_Local(Ativo):

    CNPJ = models.CharField(max_length=18, null=True, blank=True)
    # Indica quanto tempo depois do pedido a cotização de um resgate é feita
    data_cotizacao_resgate = models.DurationField()
    # Indica quanto tempo depois do pedido a liquidação de um resgate é feita
    data_liquidacao_resgate = models.DurationField()
    # Indica quanto tempo depois do pedido a cotização de uma aplicação é feita
    data_cotizacao_aplicacao = models.DurationField()
    # Indica quanto tempo depois do pedido a liquidação de uma aplicação é feita
    data_liquidacao_aplicacao = models.DurationField()
    banco = models.CharField(max_length=3, null=True, blank=True)
    agencia = models.CharField(max_length=6, null=True, blank=True)
    conta_corrente = models.CharField(max_length=7, null=True, blank=True)
    digito = models.CharField(max_length=1, null=True, blank=True)
    conta_cetip = models.CharField(max_length=10, null=True, blank=True)
    codigo_cetip = models.CharField(max_length=10, null=True, blank=True)
    # Liga o ativo fundo ao fundo do ponto de vista de gestão.
    gestao = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Fundos Locais'

    def gerido(self):
        if self.gestao == None:
            return False
        return self.gestao.gestora.anima

class Fundo_Offshore(Ativo):

    data_cotizacao_resgate = models.DurationField(null=True,blank=True)
    data_liquidacao_resgate = models.DurationField(null=True,blank=True)
    data_cotizacao_aplicacao = models.DurationField(null=True,blank=True)
    data_liquidacao_aplicacao = models.DurationField(null=True,blank=True)
    gestao = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Fundos Offshore'

    def gerido(self):
        return self.gestao.gestora.anima
