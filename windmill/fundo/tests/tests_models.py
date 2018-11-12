import datetime
import decimal
from model_mommy import mommy
import pytest
from django.test import TestCase
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
import boletagem.models as bm
import fundo.models as fm

class FundoUnitTests(TestCase):
    """
    Guarda os UnitTests do modelo Fundo
    """
    def setUp(self):
        # Gestora Anima para indicar quando uma boleta de fundo é de passivo.
        gestora = mommy.make('fundo.Gestora', anima=True)
        moeda = mommy.make('ativos.Moeda',
            nome='Real',
            codigo='BRL'
        )
        # Caixa padrão do fundo
        caixa_padrao = mommy.make('ativos.Caixa',
            nome='btg',
            moeda=moeda,
        )
        acao = mommy.make('ativos.acao',
            nome='ITSA4'
        )
        self.data_fechamento = datetime.date(year=2018, month=11, day=12)
        # Fundo gerido pela Anima.
        self.fundo = mommy.make("fundo.Fundo",
            gestora=gestora,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            caixa_padrao=caixa_padrao
        )
        # Fundo gerido como ativo.
        fundo_investido = mommy.make('ativos.Fundo_Local',
            nome=self.fundo.nome[0:24],
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=2),
            data_cotizacao_aplicacao=datetime.timedelta(days=0),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo
        )
        # Boleta de ação para ser fechada
        self.boleta_acao = mommy.make('boletagem.BoletaAcao',
            acao=acao,
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=100,
            caixa_alvo=self.fundo.caixa_padrao
        )
        # Boleta de renda fixa para ser fechada.
        self.boleta_rf_local = mommy.make('boletagem.BoletaRendaFixaLocal',
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=100,
            caixa_alvo=self.fundo.caixa_padrao,
        )
        # Boleta de renda fixa offshore para ser fechada
        self.boleta_rf_offshore = mommy.make('boletagem.BoletaRendaFixaOffshore',
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=13),
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=100,
            caixa_alvo=self.fundo.caixa_padrao,
            preco=0.9999
        )
        # Boleta de fundo local para ser fechada.
        self.boleta_fundo_local = mommy.make('boletagem.BoletaFundoLocal',
            data_operacao=self.data_fechamento,
            data_cotizacao=datetime.date(year=2018, month=11, day=12),
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            fundo=self.fundo,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            financeiro=decimal.Decimal('1000000'),
            preco=decimal.Decimal('1000'),
            caixa_alvo=self.fundo.caixa_padrao
        )
        # Boleta de fundo local com o fundo como o ativo negociado
        self.boleta_fundo_local_passivo = mommy.make('boletagem.BoletaFundoLocal',
            ativo=fundo_investido,
            data_operacao=self.data_fechamento,
            data_cotizacao=datetime.date(year=2018, month=11, day=12),
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            fundo=self.fundo,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            financeiro=decimal.Decimal('1000000'),
            preco=decimal.Decimal('1000'),
            caixa_alvo=self.fundo.caixa_padrao
        )
        self.boleta_fundo_offshore = mommy.make('boletagem.BoletaFundoOffshore',
            data_operacao=self.data_fechamento,
            data_cotizacao=datetime.date(year=2018, month=11, day=13),
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            fundo=self.fundo,
            financeiro=decimal.Decimal('1000000'),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            caixa_alvo=self.fundo.caixa_padrao,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0]
        )
    # Teste - fechar boletas de ação
    def test_fechar_boleta_acao(self):
        # Busca a boleta de ação entre os objetos do tipo BoletaAcao, com data
        # De operacao igual a 12/11/2018 - data de operação de todas as boletas.
        for boleta in bm.BoletaAcao.objects.filter(fundo=self.fundo, \
            data_operacao=datetime.date(year=2018, month=11, day=12)):
            self.assertFalse(boleta.fechado())

        self.fundo.fechar_boletas_acao(self.data_fechamento)

        for boleta in bm.BoletaAcao.objects.filter(fundo=self.fundo, \
            data_operacao=datetime.date(year=2018, month=11, day=12)):
            self.assertTrue(boleta.fechado())

    # Teste - fechar boletas de renda fixa local
    # Teste - fechar boletas de renda fixa Offshore
    # Teste - fechar boletas de fundo local
    # Teste - fechar boletas de fundo local com o fundo como ativo negociado
    # Teste - fechar boletas de fundo offshore
    # Teste - fechar boletas de fundo offshore com o fundo como ativo negociado
    # Teste - fechar boleas de passivo.
