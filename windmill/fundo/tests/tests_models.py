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
        gestora_qualquer = mommy.make('fundo.Gestora', anima=False)
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
        SPGI = mommy.make('ativos.acao',
            nome='SPGI'
        )
        V = mommy.make('ativos.acao',
            nome='V'
        )
        AMT = mommy.make('ativos.acao',
            nome='AMT'
        )
        ORLY = mommy.make('ativos.acao',
            nome='ORLY'
        )
        MA = mommy.make('ativos.acao',
            nome='MA'
        )
        CDW = mommy.make('ativos.acao',
            nome='CDW'
        )
        LIN = mommy.make('ativos.acao',
            nome='LIN'
        )
        MCO = mommy.make('ativos.acao',
            nome='MCO'
        )
        IMCD = mommy.make('ativos.acao',
            nome='IMCD'
        )
        CHTR = mommy.make('ativos.acao',
            nome='CHTR'
        )
        RB = mommy.make('ativos.acao',
            nome='RB/'
        )
        ABI = mommy.make('ativos.acao',
            nome='ABI'
        )
        SBAC = mommy.make('ativos.acao',
            nome='SBAC'
        )
        BKNG = mommy.make('ativos.acao',
            nome='BKNG'
        )
        KHC = mommy.make('ativos.acao',
            nome='KHC'
        )

        custodia = mommy.make('fundo.Custodiante')
        self.data_fechamento = datetime.date(year=2018, month=11, day=12)
        # Fundo gerido pela Anima.
        self.fundo = mommy.make("fundo.Fundo",
            gestora=gestora,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            caixa_padrao=caixa_padrao,
            custodia=custodia
        )
        self.fundo_qualquer = mommy.make("fundo.Fundo",
            gestora=gestora_qualquer,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2017, month=10, day=27),
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
        fundo_nao_investido = mommy.make('ativos.Fundo_Local',
            nome=self.fundo.nome[5:20],
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=4),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo_qualquer
        )
        fundo_off_nao_investido = mommy.make('ativos.Fundo_Offshore',
            nome=self.fundo.nome[4:15],
            data_cotizacao_resgate=datetime.timedelta(days=4),
            data_liquidacao_resgate=datetime.timedelta(days=5),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo_qualquer
        )
        # Boleta de ação para ser fechada
        boleta_acao = mommy.make('boletagem.BoletaAcao',
            acao=acao,
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=100,
            caixa_alvo=self.fundo.caixa_padrao
        )
        # Boleta de renda fixa para ser fechada.
        boleta_rf_local = mommy.make('boletagem.BoletaRendaFixaLocal',
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=100,
            caixa_alvo=self.fundo.caixa_padrao,
        )
        # Boleta de renda fixa offshore para ser fechada
        boleta_rf_offshore = mommy.make('boletagem.BoletaRendaFixaOffshore',
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=13),
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=100,
            caixa_alvo=self.fundo.caixa_padrao,
            preco=0.9999
        )
        # Boleta de fundo local para ser fechada.
        boleta_fundo_local = mommy.make('boletagem.BoletaFundoLocal',
            ativo=fundo_nao_investido,
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
            operacao=bm.BoletaFundoLocal.OPERACAO[1][0],
            financeiro=decimal.Decimal('1000000'),
            preco=decimal.Decimal('1000'),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_fundo_offshore = mommy.make('boletagem.BoletaFundoOffshore',
            ativo=fundo_off_nao_investido,
            data_operacao=self.data_fechamento,
            data_cotizacao=datetime.date(year=2018, month=11, day=13),
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            fundo=self.fundo,
            financeiro=decimal.Decimal('1000000'),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            caixa_alvo=self.fundo.caixa_padrao,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0]
        )
        boleta_fundo_offshore_2 = mommy.make('boletagem.BoletaFundoOffshore',
            data_operacao=datetime.date(year=2018, month=10, day=13),
            data_cotizacao=datetime.date(year=2018, month=10, day=13),
            data_liquidacao=datetime.date(year=2018, month=10, day=15),
            fundo=self.fundo,
            financeiro=decimal.Decimal('1500000'),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            caixa_alvo=self.fundo.caixa_padrao,
            estado=bm.BoletaFundoOffshore.ESTADO[5][0]
        )
        boleta_emprestimo = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=11, day=12),
            data_vencimento=datetime.date(year=2018, month=12, day=31),
            data_reversao=datetime.date(year=2018, month=11, day=13),
            quantidade=10000,
            fundo=self.fundo,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )
        boleta_cambio = mommy.make('boletagem.BoletaCambio',
            cambio=decimal.Decimal('3.5'),
            financeiro_origem=decimal.Decimal('35000'),
            financeiro_final=decimal.Decimal('10000'),
            data_operacao=datetime.date(year=2018, month=11, day=12),
            data_liquidacao_origem=datetime.date(year=2018, month=11, day=12),
            data_liquidacao_destino=datetime.date(year=2018, month=11, day=12)
        )
        boleta_CPR = mommy.make('boletagem.BoletaCPR',
            valor_cheio=decimal.Decimal('28.77'), # Valor cheio = (dia_trabalho_total + 1)*valor_parcial
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0], # Capitalização diária
            tipo=bm.BoletaCPR.TIPO[1][0], # Tipo diferimento
            data_inicio=datetime.date(year=2018, month=9, day=10), # No caso de diferimento, começa com o valor_cheio.
            data_vigencia_inicio=datetime.date(year=2018, month=9, day=17), # última data em que o CPR fica com seu valor cheio. Após esta data, o valor deve começar a converter para 0
            data_vigencia_fim=datetime.date(year=2018, month=10, day=17), # última data em que o CPR possui algum valor que, nesta data, deve ser igual ao valor parcial
            data_pagamento=datetime.date(year=2018, month=12, day=18), # Não faz sentido ser mais que um dia após o término da vigência, pois o valor fica zerado após a vigência.
            fundo=self.fundo
        )

        # Boleta Ação para ser fechada e criar vértices.
        self.data_carteira = datetime.date(year=2018, month=11, day=13)
        boleta_SPGI = mommy.make('boletagem.BoletaAcao',
            acao=SPGI,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=6605,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_V = mommy.make('boletagem.BoletaAcao',
            acao=V,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=9633,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_AMT = mommy.make('boletagem.BoletaAcao',
            acao=AMT,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=17397,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_ORLY = mommy.make('boletagem.BoletaAcao',
            acao=ORLY,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=10464,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_MA = mommy.make('boletagem.BoletaAcao',
            acao=MA,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=27407,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_CDW = mommy.make('boletagem.BoletaAcao',
            acao=CDW,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=38983,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_LIN = mommy.make('boletagem.BoletaAcao',
            acao=LIN,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=26602,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_MCO = mommy.make('boletagem.BoletaAcao',
            acao=MCO,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=17968,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_IMCD = mommy.make('boletagem.BoletaAcao',
            acao=IMCD,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=54290,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_CHTR = mommy.make('boletagem.BoletaAcao',
            acao=CHTR,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=10046,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_RB = mommy.make('boletagem.BoletaAcao',
            acao=RB,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=26120,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_ABI = mommy.make('boletagem.BoletaAcao',
            acao=ABI,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=56496,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_SBAC = mommy.make('boletagem.BoletaAcao',
            acao=SBAC,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=7285,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_BKNG = mommy.make('boletagem.BoletaAcao',
            acao=BKNG,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=431,
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_BKNG_3 = mommy.make('boletagem.BoletaAcao',
            acao=BKNG,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            operacao=bm.BoletaAcao.OPERACAO[1][0],
            fundo=self.fundo,
            quantidade=400,
            caixa_alvo=self.fundo.caixa_padrao
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
    def test_fechar_boleta_rf_local(self):
        # Busca a boleta de ação entre os objetos tipo BoletarendaFixaLocal

        for boleta in bm.BoletaRendaFixaLocal.objects.filter(fundo=self.fundo,\
            data_operacao=self.data_fechamento):
            self.assertFalse(boleta.fechado())

        self.fundo.fechar_boletas_rf_local(self.data_fechamento)

        for boleta in bm.BoletaRendaFixaLocal.objects.filter(fundo=self.fundo,\
            data_operacao=self.data_fechamento):
            self.assertTrue(boleta.fechado())

    # Teste - fechar boletas de renda fixa Offshore
    def test_fechar_boleta_rf_off(self):

        for boleta in bm.BoletaRendaFixaOffshore.objects.filter(fundo=self.fundo, \
            data_operacao=self.data_fechamento):
            self.assertFalse(boleta.fechado())

        self.fundo.fechar_boletas_rf_off(self.data_fechamento)

        for boleta in bm.BoletaRendaFixaOffshore.objects.filter(fundo=self.fundo, \
            data_operacao=self.data_fechamento):
            self.assertTrue(boleta.fechado())

    # Teste - fechar boletas de fundo local
    def test_fechar_boletas_fundo_local(self):
        """
        Fechamento de boletas de fundo local são diferentes. Devem ser repetida-
        mente fechadas até que todas as informações estejam disponíveis.
        Há uma boleta em que o fundo é o ativo sendo negociado.
        """
        for boleta in bm.BoletaFundoLocal.objects.filter(fundo=self.fundo, \
            data_operacao=self.data_fechamento):
            self.assertFalse(boleta.boleta_CPR.all().exists())
            self.assertFalse(boleta.boleta_provisao.all().exists())

        self.fundo.fechar_boletas_fundo_local(self.data_fechamento)

        for boleta in bm.BoletaFundoLocal.objects.filter(fundo=self.fundo, \
            data_operacao=self.data_fechamento):
            self.assertTrue(boleta.boleta_CPR.all().exists())
            self.assertTrue(boleta.boleta_provisao.all().exists())

    # Teste - fechar boletas de fundo local com o fundo como ativo negociado
    def test_fechar_boleta_fundo_local_como_ativo(self):
        """
        Faz o fechamento de boletas de fundo local com o fundo como ativo negociado.
        """
        # Verificar que não há nenhuma boleta de passivo
        self.assertFalse(bm.BoletaPassivo.objects.filter(fundo=self.fundo).exists())

        self.fundo.fechar_boletas_fundo_local_como_ativo(self.data_fechamento)
        self.assertTrue(bm.BoletaFundoLocal.objects.filter(ativo=self.boleta_fundo_local_passivo.ativo).exists())

        self.assertTrue(bm.BoletaPassivo.objects.filter(fundo=self.fundo).exists())

    # Teste - fechar boletas de fundo offshore
    def test_fechar_boleta_fundo_offshore(self):
        """
        Fechamento de boletas de fundo offshore executadas pelo fundo
        """
        # Certificando de que há a boleta de fundo offshore a ser fechada.
        query = bm.BoletaFundoOffshore.objects.filter(fundo=self.fundo).\
            exclude(estado=bm.BoletaFundoOffshore.ESTADO[5][0])

        for boleta in query:
            self.assertFalse(boleta.boleta_CPR.exists())
            self.assertFalse(boleta.boleta_provisao.exists())

        self.fundo.fechar_boletas_fundo_offshore(self.data_fechamento)

        query = bm.BoletaFundoOffshore.objects.filter(fundo=self.fundo).\
            exclude(estado=bm.BoletaFundoOffshore.ESTADO[5][0])

        for boleta in query:
            self.assertTrue(boleta.boleta_CPR.exists())
            self.assertTrue(boleta.boleta_provisao.exists())

    # Teste - fechar boletas de fundo offshore com o fundo como ativo negociado

    # Teste - fechar boletas de passivo.
    def test_fechar_boleta_passivo(self):
        for boleta in bm.BoletaPassivo.objects.filter(fundo=self.fundo, \
            data_movimentacao__lte=self.data_fechamento,\
            data_cotizacao__gte=self.data_fechamento):
            self.assertFalse(boleta.boleta_provisao.exists())
            self.assertFalse(boleta.boleta_CPR.exists())

        self.fundo.fechar_boletas_passivo(self.data_fechamento)

        for boleta in bm.BoletaPassivo.objects.filter(fundo=self.fundo, \
            data_movimentacao__lte=self.data_fechamento,\
            data_cotizacao__gte=self.data_fechamento):
            self.assertTrue(boleta.boleta_provisao.exists())
            self.assertTrue(boleta.boleta_CPR.exists())

    # Testa se o fundo fecha as boletas de empréstimo.
    def test_fechar_boleta_emprestimo(self):
        for boleta in bm.BoletaEmprestimo.objects.filter(fundo=self.fundo, \
            data_liquidacao=None):
            # Fechamento no dia de operação do emprestimo
            self.assertFalse(boleta.boleta_CPR.exists())

        self.fundo.fechar_boletas_emprestimo(self.data_fechamento)

        for boleta in bm.BoletaEmprestimo.objects.filter(fundo=self.fundo, \
            data_liquidacao=None):
            self.assertTrue(boleta.boleta_CPR.exists())
            self.assertEqual(boleta.boleta_CPR.first().valor_cheio, 0)

        fechamento = self.data_fechamento + datetime.timedelta(days=2)

        self.fundo.fechar_boletas_emprestimo(fechamento)

        for boleta in bm.BoletaEmprestimo.objects.filter(fundo=self.fundo, \
            data_liquidacao=None):
            self.assertTrue(boleta.boleta_CPR.exists())
            self.assertEqual(boleta.boleta_CPR.first().valor_cheio, boleta.financeiro(fechamento))


    def test_fechar_boleta_cambio(self):

        for boleta in bm.BoletaCambio.objects.filter(fundo=self.fundo, \
            data_operacao=self.data_fechamento):
            self.assertFalse(boleta.boleta_provisao.exists())
            self.assertFalse(boleta.boleta_CPR.exists())

        self.fundo.fechar_boletas_cambio(self.data_fechamento)

        for boleta in bm.BoletaCambio.objects.filter(fundo=self.fundo, \
            data_operacao=self.data_fechamento):
            self.assertEqual(boleta.boleta_provisao.count(),2)
            self.assertEqual(boleta.boleta_CPR.exists(), 2)

    def test_fechar_boleta_CPR(self):
        for boleta in bm.BoletaCPR.objects.filter(fundo=self.fundo, \
            data_inicio=self.data_fechamento):
            self.assertFalse(boleta.relacao_vertice.exists())

        self.fundo.fechar_boletas_CPR(self.data_fechamento)

        for boleta in bm.BoletaCPR.objects.filter(fundo=self.fundo, \
            data_inicio=self.data_fechamento):
            self.assertTrue(boleta.relacao_vertice.exists())

    def test_fechar_boleta_provisao(self):
        for boleta in bm.BoletaProvisao.objects.filter(fundo=self.fundo, \
            estado=bm.BoletaProvisao.ESTADO[0][0]):
            self.assertFalse(boleta.relacao_quantidade.exists())
            self.assertFalse(boleta.relacao_movimentacao.exists())

        self.fundo.fechar_boletas_provisao(self.data_fechamento)

        for boleta in bm.BoletaProvisao.objects.filter(fundo=self.fundo, \
            estado=bm.BoletaProvisao.ESTADO[0][0]):
            self.assertFalse(boleta.relacao_quantidade.exists())
            self.assertFalse(boleta.relacao_movimentacao.exists())

    def test_juntar_quantidades(self):
        self.fundo.fechar_boletas_do_fundo(self.data_carteira)
        self.fundo.juntar_quantidades(self.data_carteira)
        self.assertTrue(False)
        self.assertTrue(fm.Vertice.objects.filter(fundo=self.fundo, data=self.data_carteira).exists())
