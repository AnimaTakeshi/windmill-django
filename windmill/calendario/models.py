import datetime
from datetime import timedelta
import numpy as np
from django.db import models

# Create your models here.


class Feriado(models.Model):
    """
    Feriados são descritos com país, cidade e estado para estabelecer
    quais feriados devem ser usados em um calendário. Eles são usados
    como filtro para a atualização do calendário.
    """

    pais = models.ForeignKey('ativos.pais', on_delete=models.PROTECT)
    cidade = models.ForeignKey('cidade', on_delete=models.PROTECT, null=True, blank=True)
    estado = models.ForeignKey('estado', on_delete=models.PROTECT, null=True, blank=True)
    data = models.DateField()

    def __str__(self):
        return str(self.data)

class Cidade(models.Model):

    nome = models.CharField(max_length=30)
    estado = models.ForeignKey('estado', on_delete=models.PROTECT)

    def __str__(self):
        return self.nome

class Estado(models.Model):

    nome = models.CharField(max_length=30)
    pais = models.ForeignKey('ativos.pais', on_delete=models.PROTECT)

    def __str__(self):
        return self.nome

class Calendario(models.Model):
    """
    Cada calendário reflete um calendário com feriados de um determinado
    país, estado ou cidade. Calendários do nível de  cidade incluem
    feriados federais, estaduais e municipais, calendários de estado incluem
    feriados federais e estaduais, e calendários de país incluem feriados
    federais apenas.
    """

    feriados = models.ManyToManyField(Feriado)
    pais = models.ForeignKey('ativos.pais', on_delete=models.PROTECT, null=True, blank=True)
    estado = models.ForeignKey('estado', on_delete=models.PROTECT, null=True, blank=True)
    cidade = models.ForeignKey('cidade', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        descricao = ''
        if self.cidade != None:
            descricao = 'Calendário - Cidade: ' + self.cidade.nome
        elif self.estado != None:
            descricao = 'Calendário - Estado: ' + self.estado.nome
        else:
            descricao = 'Calendário - País: ' + self.pais.nome
        return descricao

    def dia_trabalho_total(self, data_inicio, data_fim):
        """
        array-like Datetime, array-like Datetime -> array-like int
        Retorna a quantidade de dias úteis entre a data de início, inclusive,
        e a data de fim, exclusive.
        """
        feriados = list(self.feriados.filter(data__gte=data_inicio,
            data__lte=data_fim).values_list('data', flat=True))
        return np.busday_count(data_inicio, data_fim, holidays=feriados)

    def dia_trabalho(self, data_referencia, dias):
        """
        array-like Datetime, array-like int -> array-like Datetime
        Retorna a data antes ou depois da data de referência, especificada pela
        variável 'dias'.
        """
        feriados = list(self.feriados.filter(data__gte=data_referencia)
            .values_list('data', flat=True))

        return np.busday_offset(data_referencia, dias, roll='backward',
            holidays=feriados).astype(datetime.datetime)

    def dias_corridos_total(self, data_inicio, data_fim):
        """
        Datetime, Datetime ->
        Retorna a quantidade de dias corridos entre a data de inicio, inclusive,
        e a data de fim, exclusive.
        """
        return (data_fim - data_inicio).days

    def dia_corrido(self, data_referencia, dias):
        """
        Retorna a data antes ou depois da data de referência, especificada pela
        variável 'dias'.
        """
        return data_referencia + timedelta(days=dias)
