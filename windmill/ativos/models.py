import datetime
from django.db import models
from django.urls import reverse

# Create your models here.
class Moeda(models.Model):
    nome = models.CharField(max_length=15, unique=True)
    codigo = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return '%s' % (self.nome)

class Pais(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    moeda = models.ForeignKey(Moeda, on_delete=models.PROTECT)

    def __str__(self):
        return '%s' % (self.nome)

class Ativo(models.Model):

    nome = models.CharField(max_length=25, unique=True)
    bbg_ticker = models.CharField(max_length=25, unique=True, null=True)
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return '%s' % (self.nome)

class Renda_Fixa(Ativo):
    TIPO_INFO_CHOICES = (
        ("PU", "PU"),
        ("YLD", "Yield")
    )
    vencimento = models.DateField(default=datetime.date.max)
    cupom = models.DecimalField(max_digits=7, decimal_places=5, null=True,
        default=0)
    info = models.CharField("informacao de mercado", max_length=3,
        choices=TIPO_INFO_CHOICES, default="PU")
    periodo = models.IntegerField("periodicidade do cupom", default=0)

class Acao(Ativo):
    TIPO_CHOICES=(
        ("PN", "Preferencial"),
        ("ON", "Ordinária")
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, null=True)

    def get_absolute_url(self):
        return reverse('ativos:detalhe_acao', args=[str(self.id)])
