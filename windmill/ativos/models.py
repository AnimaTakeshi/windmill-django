import datetime
from django.db import models

# Create your models here.
class Ativo(models.Model):

    TIPOS_DE_ATIVOS = (
        ('RV', 'Ações'),
        ('RF', 'Renda Fixa'),
        ('RE', 'Real Estate'),
        ('FRV', 'Fundo de Renda Variável'),
        ('FRF', 'Fundo de Renda Fixa'),
        ('FII', 'Fundo Imobiliário'),
    )

    nome = models.CharField(max_length=25, unique=True)
    bbg_ticker = models.CharField(max_length=25, unique=True)
    tipo_ativo = models.CharField(max_length=5, choices=TIPOS_DE_ATIVOS,
    default='RV')
    pais = models.ForeignKey('Pais', on_delete=models.PROTECT)

    class Meta:
        abstract = True
        ordering = ['nome']

    def __str__(self):
        return '%s' % (self.nome)

class Pais(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    moeda = models.ForeignKey('Moeda', on_delete=models.PROTECT)

    def __str__(self):
        return '%s' % (self.nome)

class Moeda(models.Model):
    nome = models.CharField(max_length=15, unique=True)
    codigo = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return '%s' % (self.nome)

class Renda_Fixa(Ativo):
    vencimento = models.DateField(default=datetime.date.max)
