import datetime
import decimal
from model_mommy import mommy
import pytest
from django.test import TestCase
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
import ativos.models as am
import boletagem.models as bm
import fundo.models as fm
import configuracao.models as cm

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
        dolar = mommy.make('ativos.Moeda',
            nome='Dólar',
            codigo='USD'
        )
        euro = mommy.make('ativos.moeda',
            nome='Euro',
            codigo='EUR'
        )

        libra = mommy.make('ativos.moeda',
            nome='Libra',
            codigo='GBP'
        )
        custodia = mommy.make('fundo.Custodiante',
            nome='CIBC'
        )
        custodia2 = mommy.make('fundo.Custodiante',
            nome='Pershing'
        )
        corretora = mommy.make('fundo.Corretora',
            nome='Jefferies'
        )
        # Caixa padrão do fundo
        caixa_padrao = mommy.make('ativos.Caixa',
            nome='CIBC',
            moeda=dolar,
            custodia=custodia
        )
        caixa_off = mommy.make('ativos.Caixa',
            nome='jefferies',
            moeda=dolar,
            custodia=custodia2
        )

        self.data_fechamento = datetime.date(year=2018, month=11, day=12)
        self.data_carteira = datetime.date(year=2018, month=11, day=13)
        self.data_carteira1 = datetime.date(year=2018, month=11, day=14)
        self.data_carteira2 = datetime.date(year=2018, month=11, day=15)
        self.data_carteira3 = datetime.date(year=2018, month=11, day=16)
        # Fundo gerido pela Anima.
        self.fundo = mommy.make("fundo.Fundo",
            nome='flg',
            gestora=gestora,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            caixa_padrao=caixa_padrao,
            taxa_adm_minima=decimal.Decimal('3170'),
            custodia=custodia
        )
        # Fundo não gerido
        self.fundo_qualquer = mommy.make("fundo.Fundo",
            nome='flng',
            gestora=gestora_qualquer,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2017, month=10, day=27),
            caixa_padrao=caixa_padrao
        )
        # Fundo Anima Master, gerido, que investe em outros fundos geridos
        self.fundo_master = mommy.make("fundo.Fundo",
            nome='flm',
            gestora=gestora,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2011, month=10, day=27),
            caixa_padrao=caixa_padrao,
            custodia=custodia2
        )

        # Cotista Master
        cotista_master = mommy.make('fundo.cotista',
            nome=self.fundo_master.nome,
            fundo_cotista=self.fundo_master
        )


        """
        Setup de ativos
        """

        # Ações
        acao = mommy.make('ativos.acao',
            nome='ITSA4',
            moeda=moeda
        )
        SPGI = mommy.make('ativos.acao',
            nome='SPGI',
            moeda=dolar
        )
        V = mommy.make('ativos.acao',
            nome='V',
            moeda=dolar
        )
        AMT = mommy.make('ativos.acao',
            nome='AMT',
            moeda=dolar
        )
        ORLY = mommy.make('ativos.acao',
            nome='ORLY',
            moeda=dolar
        )
        MA = mommy.make('ativos.acao',
            nome='MA',
            moeda=dolar
        )
        CDW = mommy.make('ativos.acao',
            nome='CDW',
            moeda=dolar
        )
        LIN = mommy.make('ativos.acao',
            nome='LIN',
            moeda=dolar
        )
        MCO = mommy.make('ativos.acao',
            nome='MCO',
            moeda=dolar
        )
        IMCD = mommy.make('ativos.acao',
            nome='IMCD',
            moeda=euro
        )
        CHTR = mommy.make('ativos.acao',
            nome='CHTR',
            moeda=dolar
        )
        RB = mommy.make('ativos.acao',
            nome='RB/',
            moeda=libra
        )
        ABI = mommy.make('ativos.acao',
            nome='ABI',
            moeda=euro
        )
        SBAC = mommy.make('ativos.acao',
            nome='SBAC',
            moeda=dolar

        )
        BKNG = mommy.make('ativos.acao',
            nome='BKNG',
            moeda=dolar
        )
        KHC = mommy.make('ativos.acao',
            nome='KHC',
            moeda=dolar
        )

        # Ativo fundo local gerido.
        fundo_gerido = mommy.make('ativos.Fundo_Local',
            nome=self.fundo.nome,
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=2),
            data_cotizacao_aplicacao=datetime.timedelta(days=0),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo
        )
        # Ativo fundo local não gerido
        fundo_nao_gerido = mommy.make('ativos.Fundo_Local',
            nome=self.fundo_qualquer.nome,
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=4),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo_qualquer
        )
        # Ativo Fundo off não gerido
        self.fundo_off_nao_gerido = mommy.make('ativos.Fundo_Offshore',
            nome='fundo_off_nao_gerido',
            data_cotizacao_resgate=datetime.timedelta(days=4),
            data_liquidacao_resgate=datetime.timedelta(days=5),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo_qualquer,
            moeda=dolar
        )

        # Câmbio
        eurusd = mommy.make('ativos.Cambio',
            nome='eurusd',
            bbg_ticker='eurusd curncy',
            moeda_origem=euro,
            moeda_destino=dolar,
        )

        eurusd_cmpn = mommy.make('ativos.Cambio',
            nome='eurusd cmpn',
            bbg_ticker='eurusd cmpn curncy',
            moeda_origem=euro,
            moeda_destino=dolar
        )

        gbpusd = mommy.make('ativos.Cambio',
            nome='gbpusd',
            bbg_ticker='gbpusd curncy',
            moeda_origem=libra,
            moeda_destino=dolar
        )

        bmfxtwo= mommy.make('ativos.Cambio',
            nome='brlusd',
            bbg_ticker='brlusd curncy',
            moeda_origem=moeda,
            moeda_destino=dolar
        )

        # Setup de configuração de cambio

        configuration = mommy.make('configuracao.ConfigCambio',
            fundo=self.fundo,
        )
        configuration.cambio.add(eurusd_cmpn)
        configuration.cambio.add(gbpusd)
        configuration.cambio.add(bmfxtwo)

        """
        Setup de preços
        """
        # Câmbios
        mommy.make('mercado.Preco',
            ativo=eurusd,
            preco_fechamento=1.25,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=eurusd,
            preco_fechamento=1.23,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=eurusd,
            preco_fechamento=1.22,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=eurusd,
            preco_fechamento=1.235,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=eurusd,
            preco_fechamento=1.242,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=gbpusd,
            preco_fechamento=1.5,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=gbpusd,
            preco_fechamento=1.6,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=gbpusd,
            preco_fechamento=1.55,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=gbpusd,
            preco_fechamento=1.65,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=gbpusd,
            preco_fechamento=1.53,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=bmfxtwo,
            preco_fechamento=0.30,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=bmfxtwo,
            preco_fechamento=0.31,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=bmfxtwo,
            preco_fechamento=0.29,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=bmfxtwo,
            preco_fechamento=0.28,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=bmfxtwo,
            preco_fechamento=0.295,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=eurusd_cmpn,
            preco_fechamento=1.255,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=eurusd_cmpn,
            preco_fechamento=1.235,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=eurusd_cmpn,
            preco_fechamento=1.212,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=eurusd_cmpn,
            preco_fechamento=1.2354,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=eurusd_cmpn,
            preco_fechamento=1.42,
            data_referencia=self.data_carteira3
        )

        # Ações
        mommy.make('mercado.Preco',
            ativo=acao,
            preco_fechamento=11,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=acao,
            preco_fechamento=11.1,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=acao,
            preco_fechamento=11.14,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=acao,
            preco_fechamento=11.14,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=acao,
            preco_fechamento=11.09,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=SPGI,
            preco_fechamento=182.21,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=SPGI,
            preco_fechamento=180.07,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=SPGI,
            preco_fechamento=179.08,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=SPGI,
            preco_fechamento=181.10,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=SPGI,
            preco_fechamento=181.33,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=V,
            preco_fechamento=139.72,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=V,
            preco_fechamento=139.72,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=V,
            preco_fechamento=139.49,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=V,
            preco_fechamento=141.84,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=V,
            preco_fechamento=140.18,
            data_referencia=self.data_carteira3
        )
        mommy.make('mercado.Preco',
            ativo=AMT,
            preco_fechamento=161.03,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=AMT,
            preco_fechamento=161.31,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=AMT,
            preco_fechamento=163.41,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=AMT,
            preco_fechamento=162.13,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=AMT,
            preco_fechamento=163.98,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=ORLY,
            preco_fechamento=349.41,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=ORLY,
            preco_fechamento=357.52,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=ORLY,
            preco_fechamento=354.78,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=ORLY,
            preco_fechamento=346,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=ORLY,
            preco_fechamento=352.6,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=199.14,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=198.17,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=197.58,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=200.71,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=199.04,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=CDW,
            preco_fechamento=89.19,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=CDW,
            preco_fechamento=89.64,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=CDW,
            preco_fechamento=87.23,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=CDW,
            preco_fechamento=88.56,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=CDW,
            preco_fechamento=89.44,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=LIN,
            preco_fechamento=159.22,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=LIN,
            preco_fechamento=156.93,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=LIN,
            preco_fechamento=153.36,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=LIN,
            preco_fechamento=155.18,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=LIN,
            preco_fechamento=158.08,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=MCO,
            preco_fechamento=150.07,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=MCO,
            preco_fechamento=148.06,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=MCO,
            preco_fechamento=146.36,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=MCO,
            preco_fechamento=147.46,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=MCO,
            preco_fechamento=147.25,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=IMCD,
            preco_fechamento=60.30,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=IMCD,
            preco_fechamento=61.30,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=IMCD,
            preco_fechamento=60.9,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=IMCD,
            preco_fechamento=60.40,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=IMCD,
            preco_fechamento=60,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=CHTR,
            preco_fechamento=323.35,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=CHTR,
            preco_fechamento=324.56,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=CHTR,
            preco_fechamento=320.8,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=CHTR,
            preco_fechamento=318.48,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=CHTR,
            preco_fechamento=328.54,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=RB,
            preco_fechamento=62.5,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=RB,
            preco_fechamento=62.36,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=RB,
            preco_fechamento=64.36,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=RB,
            preco_fechamento=65.09,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=RB,
            preco_fechamento=65.31,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=ABI,
            preco_fechamento=64.99,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=ABI,
            preco_fechamento=65.44,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=ABI,
            preco_fechamento=66.39,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=ABI,
            preco_fechamento=68,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=ABI,
            preco_fechamento=68.5,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=SBAC,
            preco_fechamento=171.9,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=SBAC,
            preco_fechamento=172.47,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=SBAC,
            preco_fechamento=172.04,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=SBAC,
            preco_fechamento=170.17,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=SBAC,
            preco_fechamento=172.02,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=BKNG,
            preco_fechamento=1906.28,
            data_referencia=self.data_fechamento
        )
        mommy.make('mercado.Preco',
            ativo=BKNG,
            preco_fechamento=1910.08,
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=BKNG,
            preco_fechamento=1888.37,
            data_referencia=self.data_carteira1
        )
        mommy.make('mercado.Preco',
            ativo=BKNG,
            preco_fechamento=1888.87,
            data_referencia=self.data_carteira2
        )
        mommy.make('mercado.Preco',
            ativo=BKNG,
            preco_fechamento=1855.32,
            data_referencia=self.data_carteira3
        )

        mommy.make('mercado.Preco',
            ativo=KHC,
            preco_fechamento=53.67,
            data_referencia=self.data_fechamento
        )

        mommy.make('mercado.Preco',
            ativo=fundo_gerido,
            preco_fechamento=53.67,
            data_referencia=self.data_fechamento
        )

        mommy.make('mercado.Preco',
            ativo=fundo_nao_gerido,
            preco_fechamento=1200,
            data_referencia=self.data_fechamento
        )

        mommy.make('mercado.Preco',
            ativo=caixa_off,
            preco_fechamento=1,
            data_referencia=self.data_fechamento
        )

        mommy.make('mercado.Preco',
            ativo=caixa_padrao,
            preco_fechamento=1,
            data_referencia=self.data_fechamento
        )

        """
        Setup de boletas
        """

        # Boleta de ação para ser fechada
        boleta_acao = mommy.make('boletagem.BoletaAcao',
            acao=acao,
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=15000,
            preco=decimal.Decimal('11').quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        # Boleta de renda fixa para ser fechada.
        boleta_rf_local = mommy.make('boletagem.BoletaRendaFixaLocal',
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=100,
            preco=decimal.Decimal('9300').quantize(decimal.Decimal('1.00')),
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
            ativo=fundo_nao_gerido,
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
        self.boleta_fundo_local_passivo = mommy.make('boletagem.BoletaPassivo',
            cotista=cotista_master,
            valor=decimal.Decimal('50000000'),
            data_operacao=datetime.date(year=2018, month=11, day=12),
            data_cotizacao=datetime.date(year=2018, month=11, day=12),
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            fundo=self.fundo,
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            cota=decimal.Decimal('1000').quantize(decimal.Decimal('1.00'))
        )
        self.boleta_master_investe_fundo_gerido = mommy.make('boletagem.BoletaFundoLocal',
            ativo=fundo_gerido,
            data_operacao=datetime.date(year=2018, month=11, day=12),
            data_cotizacao=datetime.date(year=2018, month=11, day=12),
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            fundo=self.fundo_master,
            operacao=bm.BoletaFundoLocal.OPERACAO[1][0],
            financeiro=decimal.Decimal('1000000'),
            preco=decimal.Decimal('2000')
        )
        boleta_fundo_offshore = mommy.make('boletagem.BoletaFundoOffshore',
            ativo=self.fundo_off_nao_gerido,
            data_operacao=self.data_fechamento,
            data_cotizacao=datetime.date(year=2018, month=11, day=13),
            data_liquidacao=datetime.date(year=2018, month=11, day=12),
            fundo=self.fundo,
            financeiro=decimal.Decimal('1000000'),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            caixa_alvo=self.fundo.caixa_padrao,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0]
        )
        # boleta_fundo_offshore_2 = mommy.make('boletagem.BoletaFundoOffshore',
        #     data_operacao=datetime.date(year=2018, month=10, day=13),
        #     data_cotizacao=datetime.date(year=2018, month=10, day=13),
        #     data_liquidacao=datetime.date(year=2018, month=10, day=15),
        #     fundo=self.fundo,
        #     financeiro=decimal.Decimal('1500000'),
        #     operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
        #     caixa_alvo=self.fundo.caixa_padrao,
        #     estado=bm.BoletaFundoOffshore.ESTADO[4][0]
        # )
        boleta_emprestimo = mommy.make('boletagem.BoletaEmprestimo',
            ativo=acao,
            data_operacao=datetime.date(year=2018, month=11, day=12),
            data_vencimento=datetime.date(year=2018, month=12, day=31),
            data_reversao=datetime.date(year=2018, month=11, day=13),
            quantidade=10000,
            fundo=self.fundo,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )

        boleta_cambio = mommy.make('boletagem.BoletaCambio',
            cambio=decimal.Decimal('1'),
            fundo=self.fundo,
            caixa_origem=self.fundo.caixa_padrao,
            caixa_destino=caixa_off,
            financeiro_origem=decimal.Decimal('10000'),
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
            data_vigencia_inicio=datetime.date(year=2018, month=9, day=17), # última data_referencia em que o CPR fica com seu valor cheio. Após esta data, o valor deve começar a converter para 0
            data_vigencia_fim=datetime.date(year=2018, month=10, day=17), # última data em que o CPR possui algum valor que, nesta data, deve ser igual ao valor parcial
            data_pagamento=datetime.date(year=2018, month=12, day=18), # Não faz sentido ser mais que um dia após o término da vigência, pois o valor fica zerado após a vigência.
            fundo=self.fundo,
            descricao="CPR TESTE"
        )

        # Boleta Ação para ser fechada e criar vértices.

        boleta_SPGI = mommy.make('boletagem.BoletaAcao',
            acao=SPGI,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=6605,
            preco=decimal.Decimal(180.07).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_V = mommy.make('boletagem.BoletaAcao',
            acao=V,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=9633,
            preco=decimal.Decimal(139.72).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_AMT = mommy.make('boletagem.BoletaAcao',
            acao=AMT,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=17397,
            preco=decimal.Decimal(161.31).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_ORLY = mommy.make('boletagem.BoletaAcao',
            acao=ORLY,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=10464,
            preco=decimal.Decimal(357.52).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_MA = mommy.make('boletagem.BoletaAcao',
            acao=MA,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=27407,
            preco=decimal.Decimal(198.17).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_CDW = mommy.make('boletagem.BoletaAcao',
            acao=CDW,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=38983,
            preco=decimal.Decimal(89.64).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_LIN = mommy.make('boletagem.BoletaAcao',
            acao=LIN,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=26602,
            preco=decimal.Decimal(156.93).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_MCO = mommy.make('boletagem.BoletaAcao',
            acao=MCO,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=17968,
            preco=decimal.Decimal(148.06).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_IMCD = mommy.make('boletagem.BoletaAcao',
            acao=IMCD,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=54290,
            preco=decimal.Decimal(61.30).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_CHTR = mommy.make('boletagem.BoletaAcao',
            acao=CHTR,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[1][0],
            fundo=self.fundo,
            quantidade=-10046,
            preco=decimal.Decimal(324.56).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_CHTR_2 = mommy.make('boletagem.BoletaAcao',
            acao=CHTR,
            data_operacao=self.data_fechamento,
            data_liquidacao=datetime.date(year=2018, month=11, day=13),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=10046,
            preco=decimal.Decimal(324.56).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_RB = mommy.make('boletagem.BoletaAcao',
            acao=RB,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=26120,
            preco=decimal.Decimal(62.36).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_ABI = mommy.make('boletagem.BoletaAcao',
            acao=ABI,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=56496,
            preco=decimal.Decimal(65.44).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_SBAC = mommy.make('boletagem.BoletaAcao',
            acao=SBAC,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=7285,
            preco=decimal.Decimal(172.47).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_BKNG = mommy.make('boletagem.BoletaAcao',
            acao=BKNG,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.fundo,
            quantidade=431,
            preco=decimal.Decimal(1910.08).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_BKNG_2 = mommy.make('boletagem.BoletaAcao',
            acao=BKNG,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia2,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[1][0],
            fundo=self.fundo,
            quantidade=31,
            preco=decimal.Decimal(1910.08).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.fundo.caixa_padrao
        )
        boleta_BKNG_3 = mommy.make('boletagem.BoletaAcao',
            acao=BKNG,
            data_operacao=self.data_carteira,
            data_liquidacao=datetime.date(year=2018, month=11, day=16),
            custodia=custodia,
            corretora=corretora,
            operacao=bm.BoletaAcao.OPERACAO[1][0],
            fundo=self.fundo,
            quantidade=400,
            preco=decimal.Decimal(1910.08).quantize(decimal.Decimal('1.00')),
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
        # Verificar que há apenas uma boleta
        self.assertEqual(bm.BoletaPassivo.objects.filter(fundo=self.fundo,).count(), 1)

        self.fundo.fechar_boletas_fundo_local_como_ativo(self.data_fechamento)
        self.assertTrue(bm.BoletaFundoLocal.objects.filter(ativo=self.boleta_master_investe_fundo_gerido.ativo).exists())

        self.assertEqual(bm.BoletaPassivo.objects.filter(fundo=self.fundo).count(), 2)

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
            data_operacao__lte=self.data_fechamento,\
            data_cotizacao__gte=self.data_fechamento):
            self.assertFalse(boleta.boleta_provisao.exists())
            self.assertFalse(boleta.boleta_CPR.exists())

        self.fundo.fechar_boletas_passivo(self.data_fechamento)

        for boleta in bm.BoletaPassivo.objects.filter(fundo=self.fundo, \
            data_operacao__lte=self.data_fechamento,\
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
            self.assertEqual(boleta.boleta_CPR.count(), 2)

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
            self.assertTrue(boleta.relacao_quantidade.exists())
            self.assertTrue(boleta.relacao_movimentacao.exists())

    # def test_juntar_quantidades(self):
    #     self.fundo.fechar_boletas_do_fundo(self.data_fechamento)
    #     self.fundo.criar_vertices(self.data_fechamento)
    #     self.fundo.consolidar_vertices(self.data_fechamento)
    #
    #     self.fundo.fechar_boletas_do_fundo(self.data_carteira)
    #     self.fundo.criar_vertices(self.data_carteira)
    #     self.fundo.consolidar_vertices(self.data_carteira)
    #
    #     mommy.make('mercado.Preco',
    #         ativo=self.fundo_off_nao_gerido,
    #         preco_fechamento=1300,
    #         data_referencia=self.data_carteira
    #     )
    #
    #     self.fundo.fechar_boletas_do_fundo(self.data_carteira1)
    #     self.fundo.criar_vertices(self.data_carteira1)
    #     self.fundo.consolidar_vertices(self.data_carteira1)
    #
    #     self.fundo.fechar_boletas_do_fundo(self.data_carteira2)
    #     self.fundo.criar_vertices(self.data_carteira2)
    #     #
    #     # self.fundo.fechar_boletas_do_fundo(self.data_carteira3)
    #     # self.fundo.criar_vertices(self.data_carteira3)
    #
    #     # self.assertTrue(False)
    #     self.assertTrue(fm.Vertice.objects.filter(fundo=self.fundo, data=self.data_carteira).exists())


class VeredaTests(TestCase):
    def setUp(self):

        self.data_carteira = datetime.date(day=23, month=11, year=2018)

        """
        Configurando moedas e países
        """
        # Moedas
        real = mommy.make('ativos.moeda',
            nome='Real Brasileiro',
            codigo='BRL'
        )
        dolar = mommy.make('ativos.moeda',
            nome='Dólar Americano',
            codigo='USD'
        )
        euro = mommy.make('ativos.moeda',
            nome='Euro',
            codigo='EUR'
        )
        libra = mommy.make('ativos.moeda',
            nome='Libra',
            codigo='GBP'
        )
        # Países
        brasil = mommy.make('ativos.pais',
            nome='Brasil',
            moeda=real
        )
        eua = mommy.make('ativos.pais',
            nome='Estados Unidos',
            moeda=dolar
        )
        holanda = mommy.make('ativos.pais',
            nome='Holanda',
            moeda=euro
        )
        uk = mommy.make('ativos.pais',
            nome='Reino Unido',
            moeda=libra
        )
        alemanha = mommy.make('ativos.pais',
            nome='Alemanha',
            moeda=euro
        )

        # CALENDARIO
        sp_state = mommy.make('calendario.estado',
            nome="São Paulo",
            pais=brasil
        )
        sp_city = mommy.make('calendario.cidade',
            nome='São Paulo',
            estado=sp_state
        )

        # Feriados
        dia1 = mommy.make('calendario.feriado',
            pais=brasil,
            cidade=sp_city,
            estado=sp_state,
            data=datetime.date(day=7, month=9, year=2018)
        )
        dia2 = mommy.make('calendario.feriado',
            pais=brasil,
            cidade=sp_city,
            estado=sp_state,
            data=datetime.date(day=12, month=10, year=2018)
        )
        dia3 = mommy.make('calendario.feriado',
            pais=brasil,
            cidade=sp_city,
            estado=sp_state,
            data=datetime.date(day=2, month=11, year=2018)
        )
        dia4 = mommy.make('calendario.feriado',
            pais=brasil,
            cidade=sp_city,
            estado=sp_state,
            data=datetime.date(day=15, month=11, year=2018)
        )
        dia5 = mommy.make('calendario.feriado',
            pais=brasil,
            cidade=sp_city,
            estado=sp_state,
            data=datetime.date(day=25, month=12, year=2018)
        )

        calendario = mommy.make('calendario.calendario',
            pais=brasil,
            estado=sp_state,
            cidade=sp_city
        )
        calendario.feriados.add(dia1)
        calendario.feriados.add(dia2)
        calendario.feriados.add(dia3)
        calendario.feriados.add(dia4)
        calendario.feriados.add(dia5)

        # FUNDO
        # Administradora
        btg_adm = mommy.make('fundo.administradora',
            nome='BTG'
        )
        maitland = mommy.make('fundo.administradora',
            nome='Maitland'
        )

        # Custodiante
        btg_cust = mommy.make('fundo.custodiante',
            nome='BTG'
        )
        itau_cust = mommy.make('fundo.custodiante',
            nome='Itaú'
        )
        persh_cust = mommy.make('fundo.custodiante',
            nome="Pershing"
        )
        cibc_cust = mommy.make('fundo.custodiante',
            nome='CIBC'
        )
        mait_cust = mommy.make('fundo.Custodiante',
            nome='Maitland'
        )

        # Corretora
        bbdc_corr = mommy.make('fundo.Corretora',
            nome='Bradesco'
        )
        jeff_corr = mommy.make('fundo.Corretora',
            nome='Jefferies'
        )
        cibc_corr = mommy.make('fundo.Corretora',
            nome='CIBC'
        )
        btg_corr = mommy.make('fundo.Corretora',
            nome='BTG'
        )
        xp_corr = mommy.make('fundo.Corretora',
            nome='XP'
        )

        # Gestora
        anima = mommy.make('fundo.gestora',
            nome='Anima',
            anima=True
        )
        pragma = mommy.make('fundo.gestora',
            nome='Pragma',
            anima=False
        )

        # ZERAGEM
        cdi = mommy.make('ativos.ativo',
            nome='CDI',
            pais=brasil,
            moeda=real,
        )

        # Caixa
        btg_cash = mommy.make('ativos.caixa',
            nome='Caixa BTG',
            pais=brasil,
            moeda=real,
            custodia=btg_cust,
            corretora=btg_corr
        )
        jeff_cash = mommy.make('ativos.caixa',
            nome='Caixa Jefferies',
            pais=eua,
            moeda=dolar,
            custodia=persh_cust,
            corretora=jeff_corr
        )
        cibc_cash = mommy.make('ativos.caixa',
            nome='Caixa CIBC',
            pais=eua,
            moeda=dolar,
            custodia=cibc_cust,
            corretora=cibc_corr
        )

        # Fundo
        self.veredas = mommy.make('fundo.fundo',
            nome='Veredas',
            administradora=btg_adm,
            gestora=anima,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(day=27,month=10,year=2014),
            pais=brasil,
            custodia=btg_cust,
            taxa_administracao=decimal.Decimal('0.06'),
            taxa_adm_minima=decimal.Decimal('3170'),
            capitalizacao_taxa_adm=fm.Fundo.CAPITALIZACAO[0][0],
            caixa_padrao=btg_cash,
            calendario=calendario
        )
        atena = mommy.make('fundo.fundo',
            nome='Atena',
            administradora=btg_adm,
            gestora=anima,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(day=31,month=12,year=2011),
            pais=brasil,
            taxa_administracao=decimal.Decimal('0.06'),
            capitalizacao_taxa_adm=fm.Fundo.CAPITALIZACAO[0][0],
            caixa_padrao=btg_cash,
        )

        rocas = mommy.make('fundo.fundo',
            nome='Rocas',
            administradora=maitland,
            gestora=anima,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(day=21,month=6,year=2018),
            pais=eua,
            taxa_administracao=decimal.Decimal('0.05'),
            capitalizacao_taxa_adm=fm.Fundo.CAPITALIZACAO[1][0],
            caixa_padrao=cibc_cash,
        )

        # Cotista
        atena_cotista = mommy.make('fundo.Cotista',
            nome='ATENA',
            cota_media=decimal.Decimal(1884.0957132),
            fundo_cotista=atena
        )

        # ATIVOS
        # Ação
        ABEV = mommy.make('ativos.Acao',
            nome='ABEV3',
            bbg_ticker='ABEV3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        ITSA = mommy.make('ativos.Acao',
            nome='ITSA4',
            bbg_ticker='ITSA4 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        ITUB = mommy.make('ativos.Acao',
            nome='ITUB4',
            bbg_ticker='ITUB4 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        LAME = mommy.make('ativos.Acao',
            nome='LAME3',
            bbg_ticker='LAME3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        LREN = mommy.make('ativos.Acao',
            nome='LREN3',
            bbg_ticker='LREN3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        NATU = mommy.make('ativos.Acao',
            nome='NATU3',
            bbg_ticker='NATU3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        RADL = mommy.make('ativos.Acao',
            nome='RADL3',
            bbg_ticker='RADL3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        UGPA = mommy.make('ativos.Acao',
            nome='UGPA3',
            bbg_ticker='UGPA3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        WEGE = mommy.make('ativos.Acao',
            nome='WEGE',
            bbg_ticker='WEGE BZ EQUITY',
            pais=brasil,
            moeda=real
        )

        # Renda fixa
        lft20240901 = mommy.make('ativos.Renda_Fixa',
            nome='LFT 20240901',
            pais=brasil,
            moeda=real,
            vencimento=datetime.date(day=1,month=9,year=2024),
            cupom=decimal.Decimal('0'),
            periodo=decimal.Decimal('0'),
            info=am.Renda_Fixa.TIPO_INFO_CHOICES[0][0]
        )
        lft20240301 = mommy.make('ativos.Renda_Fixa',
            nome='LFT 20240301',
            pais=brasil,
            moeda=real,
            vencimento=datetime.date(day=1,month=3,year=2024),
            cupom=decimal.Decimal('0'),
            periodo=decimal.Decimal('0'),
            info=am.Renda_Fixa.TIPO_INFO_CHOICES[0][0]
        )
        lft20230901 = mommy.make('ativos.Renda_Fixa',
            nome='LFT 20230901',
            pais=brasil,
            moeda=real,
            vencimento=datetime.date(day=1,month=9,year=2023),
            cupom=decimal.Decimal('0'),
            periodo=decimal.Decimal('0'),
            info=am.Renda_Fixa.TIPO_INFO_CHOICES[0][0]
        )
        tbill20181129 = mommy.make('ativos.Renda_Fixa',
            nome='T-BILL 20181129',
            pais=eua,
            moeda=dolar,
            vencimento=datetime.date(day=29,month=11,year=2018),
            cupom=decimal.Decimal('0'),
            periodo=decimal.Decimal('0'),
            info=am.Renda_Fixa.TIPO_INFO_CHOICES[1][0]
        )
        tbill20190110 = mommy.make('ativos.Renda_Fixa',
            nome='T-BILL 20190110',
            pais=eua,
            moeda=dolar,
            vencimento=datetime.date(day=10,month=1,year=2019),
            cupom=decimal.Decimal('0'),
            periodo=decimal.Decimal('0'),
            info=am.Renda_Fixa.TIPO_INFO_CHOICES[1][0]
        )
        bmfxclco = mommy.make('ativos.Cambio',
            nome='BMFXCLCO',
            bbg_ticker='BMFXCLCO INDEX',
            moeda_origem=dolar,
            moeda_destino=real
        )
        # Fundos locais
        honor = mommy.make('ativos.Fundo_Local',
            nome='HONOR MASTER',
            bbg_ticker='HONMSTR BZ EQUITY',
            moeda=real,
            pais=brasil,
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=4),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
        )
        soberano = mommy.make('ativos.Fundo_Local',
            nome='SOBERANO',
            bbg_ticker='ITAUSOB BZ EQUITY',
            moeda=real,
            pais=brasil,
            data_cotizacao_resgate=datetime.timedelta(days=0),
            data_liquidacao_resgate=datetime.timedelta(days=0),
            data_cotizacao_aplicacao=datetime.timedelta(days=0),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
        )
        # Fundos off
        rocas_ativo = mommy.make('ativos.Fundo_Offshore',
            nome='ROCAS LIMITED',
            gestao=rocas,
            moeda=dolar,
            pais=eua
        )

        """
        Configuracao de cambio
        """

        configuration = mommy.make('configuracao.ConfigCambio',
            fundo=self.veredas,
        )
        configuration.cambio.add(bmfxclco)

        config_zeragem = mommy.make('configuracao.ConfigZeragem',
            fundo=self.veredas,
            caixa=btg_cash,
            indice_zeragem=cdi
        )

        """
        Preços de mercado
        """
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(0.999754).quantize(decimal.Decimal('1.000000')),
            data_referencia=datetime.date(year=2018, month=11, day=22)
        )


        mommy.make('mercado.Preco',
            ativo=ABEV,
            preco_fechamento=decimal.Decimal(16.2).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=ITSA,
            preco_fechamento=decimal.Decimal(11.86).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=ITUB,
            preco_fechamento=decimal.Decimal(34.57).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=LAME,
            preco_fechamento=decimal.Decimal(13.65).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=LREN,
            preco_fechamento=decimal.Decimal(39.23).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=NATU,
            preco_fechamento=decimal.Decimal(38.42).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=RADL,
            preco_fechamento=decimal.Decimal(62.71).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=UGPA,
            preco_fechamento=decimal.Decimal(45.6).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=WEGE,
            preco_fechamento=decimal.Decimal(17.68).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=lft20230901,
            preco_fechamento=decimal.Decimal(9813.007311).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=lft20240301,
            preco_fechamento=decimal.Decimal(9810.513074).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=lft20240901,
            preco_fechamento=decimal.Decimal(9808.932081).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=tbill20181129,
            preco_fechamento=decimal.Decimal(0.999649).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=tbill20190110,
            preco_fechamento=decimal.Decimal(0.996538).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=honor,
            preco_fechamento=decimal.Decimal(26.2372346).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=soberano,
            preco_fechamento=decimal.Decimal(44.746354).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=bmfxclco,
            preco_fechamento=decimal.Decimal(3.8181).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=rocas_ativo,
            preco_fechamento=decimal.Decimal(992.733).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(1.000).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )

        self.data_carteira_1 = datetime.date(day=26,month=11,year=2018)

        mommy.make('mercado.Preco',
            ativo=ABEV,
            preco_fechamento=decimal.Decimal(16.15).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=ITSA,
            preco_fechamento=decimal.Decimal(11.64).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=ITUB,
            preco_fechamento=decimal.Decimal(34).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=LAME,
            preco_fechamento=decimal.Decimal(13.41).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=LREN,
            preco_fechamento=decimal.Decimal(38.03).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=NATU,
            preco_fechamento=decimal.Decimal(38.53).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=RADL,
            preco_fechamento=decimal.Decimal(62.17).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=UGPA,
            preco_fechamento=decimal.Decimal(45.25).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=WEGE,
            preco_fechamento=decimal.Decimal(17.74).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=lft20230901,
            preco_fechamento=decimal.Decimal(9815.472385).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=lft20240301,
            preco_fechamento=decimal.Decimal(9812.928422).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=lft20240901,
            preco_fechamento=decimal.Decimal(9811.238996).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=tbill20181129,
            preco_fechamento=decimal.Decimal(0.999826).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=tbill20190110,
            preco_fechamento=decimal.Decimal(0.996737).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=honor,
            preco_fechamento=decimal.Decimal(26.0931743).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=soberano,
            preco_fechamento=decimal.Decimal(44.757101).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=bmfxclco,
            preco_fechamento=decimal.Decimal(3.9062).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(1.000246).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_1
        )

        self.data_carteira_2 = datetime.date(day=27,month=11,year=2018)

        mommy.make('mercado.Preco',
            ativo=ABEV,
            preco_fechamento=decimal.Decimal(16.54).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=ITSA,
            preco_fechamento=decimal.Decimal(12.09).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=ITUB,
            preco_fechamento=decimal.Decimal(35.15).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=LAME,
            preco_fechamento=decimal.Decimal(13.72).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=LREN,
            preco_fechamento=decimal.Decimal(39.49).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=NATU,
            preco_fechamento=decimal.Decimal(38.25).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=RADL,
            preco_fechamento=decimal.Decimal(62.8).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=UGPA,
            preco_fechamento=decimal.Decimal(46.1).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=WEGE,
            preco_fechamento=decimal.Decimal(18.05).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=lft20230901,
            preco_fechamento=decimal.Decimal(9817.888955).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=lft20240301,
            preco_fechamento=decimal.Decimal(9815.35419).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=lft20240901,
            preco_fechamento=decimal.Decimal(9813.713471).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=tbill20181129,
            preco_fechamento=decimal.Decimal(0.999883).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=tbill20190110,
            preco_fechamento=decimal.Decimal(0.996809).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=honor,
            preco_fechamento=decimal.Decimal(26.6569745).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=soberano,
            preco_fechamento=decimal.Decimal(44.767854).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=bmfxclco,
            preco_fechamento=decimal.Decimal(3.8947).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(1.00049246).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )

        """
        Boletas de ativos
        """
        # Boleta Aporte
        boleta_passivo = mommy.make('boletagem.BoletaPassivo',
            cotista=atena_cotista,
            valor=decimal.Decimal(860178738.36).quantize(decimal.Decimal('1.00')),
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            fundo=self.veredas,
            cota=1882.05526286,
        )

        # Boletas ações
        boleta_ABEV = mommy.make('boletagem.BoletaAcao',
            acao=ABEV,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=745300,
            preco=decimal.Decimal(16.2).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_ITSA = mommy.make('boletagem.BoletaAcao',
            acao=ITSA,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=188124,
            preco=decimal.Decimal(11.86).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_ITSA = mommy.make('boletagem.BoletaAcao',
            acao=ITSA,
            data_operacao=self.data_carteira_2,
            data_liquidacao=datetime.date(day=3, month=12, year=2018),
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[1][0],
            fundo=self.veredas,
            quantidade=188124,
            preco=decimal.Decimal(11.69).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_ITUB = mommy.make('boletagem.BoletaAcao',
            acao=ITUB,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=186494,
            preco=decimal.Decimal(34.57).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_ITUB2 = mommy.make('boletagem.BoletaAcao',
            acao=ITUB,
            data_operacao=self.data_carteira_2,
            data_liquidacao=datetime.date(day=3, month=12, year=2018),
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[1][0],
            fundo=self.veredas,
            quantidade=92000,
            preco=decimal.Decimal(34.25).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_LAME = mommy.make('boletagem.BoletaAcao',
            acao=LAME,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=610560,
            preco=decimal.Decimal(13.65).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_LAME_2 = mommy.make('boletagem.BoletaAcao',
            acao=LAME,
            data_operacao=self.data_carteira_2,
            data_liquidacao=datetime.date(day=3, month=12, year=2018),
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=58500,
            preco=decimal.Decimal(13.57).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_LREN = mommy.make('boletagem.BoletaAcao',
            acao=LREN,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=247630,
            preco=decimal.Decimal(39.23).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_NATU = mommy.make('boletagem.BoletaAcao',
            acao=NATU,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=itau_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=10320689,
            preco=decimal.Decimal(38.42).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_RADL = mommy.make('boletagem.BoletaAcao',
            acao=RADL,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=itau_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=1880655,
            preco=decimal.Decimal(62.71).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_UGPA = mommy.make('boletagem.BoletaAcao',
            acao=UGPA,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=152800,
            preco=decimal.Decimal(45.6).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_WEGE = mommy.make('boletagem.BoletaAcao',
            acao=WEGE,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=393138,
            preco=decimal.Decimal(17.68).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_WEGE2 = mommy.make('boletagem.BoletaAcao',
            acao=WEGE,
            data_operacao=self.data_carteira_2,
            data_liquidacao=datetime.date(day=3, month=12, year=2018),
            custodia=btg_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.veredas,
            quantidade=115300,
            preco=decimal.Decimal(17.78).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.veredas.caixa_padrao
        )

        # Boletas Renda Fixa
        boleta_LFT20240901 = mommy.make('boletagem.BoletaRendaFixaLocal',
            ativo=lft20240901,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            corretora=xp_corr,
            custodia=btg_cust,
            fundo=self.veredas,
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=1050,
            preco=decimal.Decimal(9808.932081).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.0025).quantize(decimal.Decimal('1.000000')),
            corretagem=0,
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_LFT20240301 = mommy.make('boletagem.BoletaRendaFixaLocal',
            ativo=lft20240301,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            corretora=xp_corr,
            custodia=btg_cust,
            fundo=self.veredas,
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=601,
            preco=decimal.Decimal(9810.513074).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.0025).quantize(decimal.Decimal('1.000000')),
            corretagem=0,
            caixa_alvo=self.veredas.caixa_padrao
        )
        boleta_LFT20230901 = mommy.make('boletagem.BoletaRendaFixaLocal',
            ativo=lft20230901,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            corretora=xp_corr,
            custodia=btg_cust,
            fundo=self.veredas,
            operacao=bm.BoletaRendaFixaLocal.OPERACAO[0][0],
            quantidade=1964,
            preco=decimal.Decimal(9813.007311).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.0025).quantize(decimal.Decimal('1.000000')),
            corretagem=0,
            caixa_alvo=self.veredas.caixa_padrao
        )

        # Boletas Fundos locais
        boleta_Honor = mommy.make('boletagem.BoletaFundoLocal',
            ativo=honor,
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            fundo=self.veredas,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            liquidacao=bm.BoletaFundoLocal.TIPO_LIQUIDACAO[1][0],
            financeiro=decimal.Decimal(38472592.35).quantize(decimal.Decimal('1.00')),
            quantidade=decimal.Decimal(1466335.64628).quantize(decimal.Decimal('1.00000')),
            preco=decimal.Decimal(26.237235).quantize(decimal.Decimal('1.000000')),
            caixa_alvo=self.veredas.caixa_padrao,
            custodia=itau_cust
        )
        boleta_Soberano = mommy.make('boletagem.BoletaFundoLocal',
            ativo=soberano,
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            fundo=self.veredas,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            liquidacao=bm.BoletaFundoLocal.TIPO_LIQUIDACAO[1][0],
            financeiro=decimal.Decimal(254478.18).quantize(decimal.Decimal('1.00')),
            quantidade=decimal.Decimal(5687.126596).quantize(decimal.Decimal('1.000000')),
            preco=decimal.Decimal(44.746354).quantize(decimal.Decimal('1.000000')),
            caixa_alvo=self.veredas.caixa_padrao,
            custodia=itau_cust
        )

        # Boleta Câmbio
        boleta_cambio = mommy.make('boletagem.BoletaCambio',
            cambio=decimal.Decimal('3.8181'),
            fundo=self.veredas,
            caixa_origem=self.veredas.caixa_padrao,
            caixa_destino=jeff_cash,
            financeiro_origem=decimal.Decimal('218777210.82'),
            financeiro_final=decimal.Decimal('57300021.17'),
            data_operacao=self.data_carteira,
            data_liquidacao_origem=self.data_carteira,
            data_liquidacao_destino=self.data_carteira
        )

        # Boleta fundo Off
        boleta_Rocas = mommy.make('boletagem.BoletaFundoOffshore',
            ativo=rocas_ativo,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0],
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            fundo=self.veredas,
            financeiro=decimal.Decimal(22812938.82).quantize(decimal.Decimal('1.00')),
            preco=decimal.Decimal(992.733).quantize(decimal.Decimal('1.000')),
            quantidade=decimal.Decimal(22979.934).quantize(decimal.Decimal('1.000')),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            caixa_alvo=jeff_cash,
            custodia=mait_cust,
        )

        # Boleta Renda Fixa Off
        boleta_TBILL2018 = mommy.make('boletagem.BoletaRendaFixaOffshore',
            ativo=tbill20181129,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            corretora=jeff_corr,
            custodia=persh_cust,
            corretagem=0,
            fundo=self.veredas,
            operacao=bm.BoletaRendaFixaOffshore.OPERACAO[0][0],
            quantidade=4540000,
            preco=0.999649,
            caixa_alvo=jeff_cash,
        )
        boleta_TBILL2019 = mommy.make('boletagem.BoletaRendaFixaOffshore',
            ativo=tbill20190110,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            corretora=jeff_corr,
            custodia=persh_cust,
            corretagem=0,
            fundo=self.veredas,
            operacao=bm.BoletaRendaFixaOffshore.OPERACAO[0][0],
            quantidade=30000000,
            preco=0.996538,
            caixa_alvo=jeff_cash,
        )
        boleta_CPR_Anbima = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa Anbima 10.2018 - DIFERIMENTO",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(1047).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=26, month=10, year=2018),
            data_vigencia_inicio=datetime.date(day=26, month=10, year=2018),
            data_vigencia_fim=datetime.date(day=26, month=12, year=2018),
            data_pagamento=datetime.date(day=26, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[1][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )
        boleta_CPR_CVM = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa CVM 10.2018 - DIFERIMENTO",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(15036.9).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=8, month=10, year=2018),
            data_vigencia_inicio=datetime.date(day=8, month=10, year=2018),
            data_vigencia_fim=datetime.date(day=8, month=1, year=2019),
            data_pagamento=datetime.date(day=8, month=1, year=2019),
            tipo=bm.BoletaCPR.TIPO[1][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )
        boleta_CPR_SELIC = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa SELIC 10.2018 - DIFERIMENTO",
            fundo=self.veredas,
            valor_parcial=decimal.Decimal(-1.37).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=19, month=11, year=2018),
            data_vigencia_inicio=datetime.date(day=19, month=11, year=2018),
            data_vigencia_fim=datetime.date(day=19, month=12, year=2018),
            data_pagamento=datetime.date(day=19, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[1][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )
        boleta_CPR_Audit = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa Auditoria 03.2017 - DIFERIMENTO",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(-1160.45).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=26, month=7, year=2018),
            data_vigencia_inicio=datetime.date(day=26, month=7, year=2018),
            data_vigencia_fim=datetime.date(day=25, month=7, year=2019),
            data_pagamento=datetime.date(day=25, month=7, year=2019),
            tipo=bm.BoletaCPR.TIPO[1][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )
        boleta_CPR_Audit2 = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa Auditoria 03.2018 - DIFERIMENTO",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(7876.06).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=24, month=8, year=2018),
            data_vigencia_inicio=datetime.date(day=24, month=8, year=2018),
            data_vigencia_fim=datetime.date(day=23, month=8, year=2019),
            data_pagamento=datetime.date(day=23, month=8, year=2019),
            tipo=bm.BoletaCPR.TIPO[1][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )
        boleta_CPR_SELIC2 = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa SELIC 11.2018 - Acúmulo",
            fundo=self.veredas,
            valor_parcial=decimal.Decimal(-5.41).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=1, month=11, year=2018),
            data_vigencia_inicio=datetime.date(day=1, month=11, year=2018),
            data_vigencia_fim=datetime.date(day=30, month=11, year=2018),
            data_pagamento=datetime.date(day=30, month=11, year=2018),
            tipo=bm.BoletaCPR.TIPO[0][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )
        boleta_CPR_Administracao = mommy.make('boletagem.BoletaCPR',
            descricao="Taxa de Administração 11.2018",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal('-27656.98').quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=1, month=11, year=2018),
            data_vigencia_inicio=datetime.date(day=1, month=11, year=2018),
            data_vigencia_fim=datetime.date(day=30, month=11, year=2018),
            data_pagamento=datetime.date(day=7, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[4][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )

        vertice_taxa_adm = mommy.make('fundo.Vertice',
            fundo=self.veredas,
            custodia=btg_cust,
            corretora=btg_corr,
            quantidade=1,
            valor=decimal.Decimal('-27656.98'),
            preco=1,
            movimentacao=0,
            data=datetime.date(day=22, month=11, year=2018),
            cambio=1,
            content_object=boleta_CPR_Administracao
        )

        carteira = mommy.make('fundo.carteira',
            fundo=self.veredas,
            data=datetime.date(day=22, month=11, year=2018),
            cota=decimal.Decimal('1884.684601'),
            pl=decimal.Decimal('861380457.16'),
            movimentacao=0
        )

        boleta_CPR_DVD_ITUB = mommy.make('boletagem.BoletaCPR',
            descricao="Dividendos ITUB4",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(1864.95).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=1, month=11, year=2018),
            data_pagamento=datetime.date(day=3, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_ITUB = mommy.make('boletagem.BoletaProvisao',
            descricao="Dividendos ITUB4",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_ITUB.data_pagamento,
            financeiro=boleta_CPR_DVD_ITUB.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_LREN1 = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP LREN3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(16725.54).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=21, month=3, year=2018),
            data_pagamento=datetime.date(day=31, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_LREN1 = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP LREN3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_LREN1.data_pagamento,
            financeiro=boleta_CPR_DVD_LREN1.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_LREN2 = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP LREN3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(18137.16).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=25, month=6, year=2018),
            data_pagamento=datetime.date(day=31, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_LREN2 = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP LREN3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_LREN2.data_pagamento,
            financeiro=boleta_CPR_DVD_LREN2.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_LREN3 = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP LREN3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(19732.4).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=25, month=9, year=2018),
            data_pagamento=datetime.date(day=31, month=12, year=2099),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_LREN3 = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP LREN3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_LREN3.data_pagamento,
            financeiro=boleta_CPR_DVD_LREN3.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_WEGE = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP WEGE3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(15447.96).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=24, month=9, year=2018),
            data_pagamento=datetime.date(day=13, month=3, year=2019),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_WEGE = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP WEGE3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_WEGE.data_pagamento,
            financeiro=boleta_CPR_DVD_WEGE.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_RADL1 = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP RADL3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(296940.38).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=27, month=9, year=2018),
            data_pagamento=datetime.date(day=31, month=5, year=2019),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_RADL1 = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP RADL3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_RADL1.data_pagamento,
            financeiro=boleta_CPR_DVD_RADL1.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_RADL2 = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP RADL3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(288374).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=27, month=6, year=2018),
            data_pagamento=datetime.date(day=3, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_RADL2 = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP RADL3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_RADL2.data_pagamento,
            financeiro=boleta_CPR_DVD_RADL2.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_RADL3 = mommy.make('boletagem.BoletaCPR',
            descricao="JSCP RADL3",
            fundo=self.veredas,
            valor_cheio=decimal.Decimal(291228.83).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=27, month=3, year=2018),
            data_pagamento=datetime.date(day=3, month=12, year=2018),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_RADL3 = mommy.make('boletagem.BoletaProvisao',
            descricao="JSCP RADL3",
            fundo=self.veredas,
            caixa_alvo=self.veredas.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_RADL3.data_pagamento,
            financeiro=boleta_CPR_DVD_RADL3.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        # BOLETAS EMPRÉSTIMOS
        boleta_emprestimo_abev1 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ABEV,
            data_operacao=datetime.date(day=3,month=9,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=4,month=9,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=31682,
            taxa=0.1,
            preco=18.84,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_abev2 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ABEV,
            data_operacao=datetime.date(day=3,month=9,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=4,month=9,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=9300,
            taxa=0.1,
            preco=18.84,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_abev3 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ABEV,
            data_operacao=datetime.date(day=19,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=2,month=1,year=2019),
            reversivel=True,
            data_reversao=datetime.date(day=21,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=173900,
            taxa=0.04,
            preco=16.27,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_abev4 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ABEV,
            data_operacao=datetime.date(day=19,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=2,month=1,year=2019),
            reversivel=True,
            data_reversao=datetime.date(day=21,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=76100,
            taxa=0.04,
            preco=16.27,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_itub1 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ITUB,
            data_operacao=datetime.date(day=12,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=13,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=4078,
            taxa=0.07,
            preco=50.32,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_itub2 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ITUB,
            data_operacao=datetime.date(day=23,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=26,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=14343,
            taxa=0.07,
            preco=34.68,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_itub3 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=ITUB,
            data_operacao=datetime.date(day=23,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=26,month=12,year=2089),
            reversivel=True,
            data_reversao=datetime.date(day=26,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=28950,
            taxa=0.09,
            preco=34.68,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_lame = mommy.make('boletagem.BoletaEmprestimo',
            ativo=LAME,
            data_operacao=datetime.date(day=23,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=22,month=4,year=2019),
            reversivel=True,
            data_reversao=datetime.date(day=26,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=5100,
            taxa=0.5,
            preco=13.44,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_ugpa1 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=UGPA,
            data_operacao=datetime.date(day=31,month=10,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=12,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=1,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=36285,
            taxa=0.15,
            preco=44.5,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_ugpa2 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=UGPA,
            data_operacao=datetime.date(day=7,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=18,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=8,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=2700,
            taxa=0.18,
            preco=42.73,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_ugpa3 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=UGPA,
            data_operacao=datetime.date(day=12,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=13,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=45000,
            taxa=0.13,
            preco=40.61,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_ugpa4 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=UGPA,
            data_operacao=datetime.date(day=16,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=28,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=19,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=215,
            taxa=0.13,
            preco=40.39,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_ugpa5 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=UGPA,
            data_operacao=datetime.date(day=16,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=28,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=19,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=20000,
            taxa=0.13,
            preco=40.39,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_ugpa6 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=UGPA,
            data_operacao=datetime.date(day=16,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=28,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=19,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=78,
            taxa=0.13,
            preco=40.39,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege1 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=22,month=10,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=3,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=23,month=10,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=3608,
            taxa=0.22,
            preco=18.55,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege2 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=12,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=13,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=601,
            taxa=0.21,
            preco=18.49,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege3 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=12,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=13,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=136,
            taxa=0.21,
            preco=18.49,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege4 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=12,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=21,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=13,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=99999,
            taxa=0.2,
            preco=18.49,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege5 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=16,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=28,month=12,year=2018),
            reversivel=True,
            data_reversao=datetime.date(day=19,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=19,
            taxa=0.2,
            preco=18.32,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege6 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=21,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=3,month=1,year=2019),
            reversivel=True,
            data_reversao=datetime.date(day=22,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=151497,
            taxa=0.17,
            preco=18.16,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )
        boleta_emprestimo_wege7 = mommy.make('boletagem.BoletaEmprestimo',
            ativo=WEGE,
            data_operacao=datetime.date(day=21,month=11,year=2018),
            fundo=self.veredas,
            corretora=btg_corr,
            custodia=btg_cust,
            data_vencimento=datetime.date(day=3,month=1,year=2019),
            reversivel=True,
            data_reversao=datetime.date(day=22,month=11,year=2018),
            operacao=bm.BoletaEmprestimo.OPERACAO[0][0],
            comissao=decimal.Decimal(0),
            quantidade=2297,
            taxa=0.17,
            preco=18.16,
            caixa_alvo=self.veredas.caixa_padrao,
            calendario=calendario
        )

        # Boleta Renda Fixa Off
        boleta_venda_TBILL2018 = mommy.make('boletagem.BoletaRendaFixaOffshore',
            ativo=tbill20181129,
            data_operacao=self.data_carteira_1,
            data_liquidacao=self.data_carteira_2,
            corretora=jeff_corr,
            custodia=persh_cust,
            corretagem=3.5,
            fundo=self.veredas,
            operacao=bm.BoletaRendaFixaOffshore.OPERACAO[1][0],
            quantidade=4420000,
            preco=0.999732,
            caixa_alvo=jeff_cash,
        )

    def test_juntar_quantidades(self):
        self.veredas.zeragem_de_caixa(self.data_carteira)
        self.veredas.verificar_proventos(self.data_carteira)
        self.veredas.fechar_boletas_do_fundo(self.data_carteira)
        self.veredas.criar_vertices(self.data_carteira)
        self.veredas.consolidar_vertices(self.data_carteira)
        self.veredas.calcular_cota(self.data_carteira)

        self.assertTrue(fm.Carteira.objects.filter(data=self.data_carteira).exists())

        self.veredas.zeragem_de_caixa(self.data_carteira_1)
        self.veredas.verificar_proventos(self.data_carteira_1)
        self.veredas.fechar_boletas_do_fundo(self.data_carteira_1)
        self.veredas.criar_vertices(self.data_carteira_1)
        self.veredas.consolidar_vertices(self.data_carteira_1)
        self.veredas.calcular_cota(self.data_carteira_1)

        self.veredas.zeragem_de_caixa(self.data_carteira_2)
        self.veredas.verificar_proventos(self.data_carteira_2)
        self.veredas.fechar_boletas_do_fundo(self.data_carteira_2)
        self.veredas.criar_vertices(self.data_carteira_2)
        self.veredas.consolidar_vertices(self.data_carteira_2)
        self.veredas.calcular_cota(self.data_carteira_2)


        # self.fundo.fechar_boletas_do_fundo(self.data_carteira3)
        # self.fundo.criar_vertices(self.data_carteira3)

        # self.assertTrue(False)
        # self.assertTrue(fm.Vertice.objects.filter(fundo=self.veredas, data=self.data_carteira).exists())


class ItatiaiaTests(TestCase):
    def setUp(self):
        # Moedas
        real = mommy.make('ativos.moeda',
            nome='Real Brasileiro',
            codigo='BRL'
        )
        dolar = mommy.make('ativos.moeda',
            nome='Dólar Americano',
            codigo='USD'
        )
        euro = mommy.make('ativos.moeda',
            nome='Euro',
            codigo='EUR'
        )
        libra = mommy.make('ativos.moeda',
            nome='Libra',
            codigo='GBP'
        )
        # Países
        brasil = mommy.make('ativos.pais',
            nome='Brasil',
            moeda=real
        )
        eua = mommy.make('ativos.pais',
            nome='Estados Unidos',
            moeda=dolar
        )
        holanda = mommy.make('ativos.pais',
            nome='Holanda',
            moeda=euro
        )
        uk = mommy.make('ativos.pais',
            nome='Reino Unido',
            moeda=libra
        )
        alemanha = mommy.make('ativos.pais',
            nome='Alemanha',
            moeda=euro
        )

        # CALENDARIO
        sp_state = mommy.make('calendario.estado',
            nome="São Paulo",
            pais=brasil
        )
        sp_city = mommy.make('calendario.cidade',
            nome='São Paulo',
            estado=sp_state
        )

        # FUNDO
        # Administradora
        btg_adm = mommy.make('fundo.administradora',
            nome='BTG'
        )
        maitland = mommy.make('fundo.administradora',
            nome='Maitland'
        )

        # Custodiante
        btg_cust = mommy.make('fundo.custodiante',
            nome='BTG'
        )
        itau_cust = mommy.make('fundo.custodiante',
            nome='Itaú'
        )
        persh_cust = mommy.make('fundo.custodiante',
            nome="Pershing"
        )
        cibc_cust = mommy.make('fundo.custodiante',
            nome='CIBC'
        )
        mait_cust = mommy.make('fundo.Custodiante',
            nome='Maitland'
        )

        # Corretora
        bbdc_corr = mommy.make('fundo.Corretora',
            nome='Bradesco'
        )
        jeff_corr = mommy.make('fundo.Corretora',
            nome='Jefferies'
        )
        cibc_corr = mommy.make('fundo.Corretora',
            nome='CIBC'
        )
        btg_corr = mommy.make('fundo.Corretora',
            nome='BTG'
        )
        xp_corr = mommy.make('fundo.Corretora',
            nome='XP'
        )

        # Gestora
        anima = mommy.make('fundo.gestora',
            nome='Anima',
            anima=True
        )
        pragma = mommy.make('fundo.gestora',
            nome='Pragma',
            anima=False
        )

        # ZERAGEM
        cdi = mommy.make('ativos.ativo',
            nome='CDI',
            pais=brasil,
            moeda=real,
        )

        # Caixa
        btg_cash = mommy.make('ativos.caixa',
            nome='Caixa BTG',
            pais=brasil,
            moeda=real,
            custodia=btg_cust,
            corretora=btg_corr,
        )
        jeff_cash = mommy.make('ativos.caixa',
            nome='Caixa JEFF',
            pais=eua,
            moeda=dolar,
            custodia=persh_cust,
            corretora=jeff_corr,
        )

        # Fundo
        self.itatiaia = mommy.make('fundo.fundo',
            nome='ITATIAIA',
            administradora=btg_adm,
            gestora=anima,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(day=27,month=10,year=2014),
            pais=brasil,
            custodia=btg_cust,
            taxa_administracao=decimal.Decimal('0.06'),
            taxa_adm_minima=decimal.Decimal('3170'),
            capitalizacao_taxa_adm=fm.Fundo.CAPITALIZACAO[0][0],
            caixa_padrao=btg_cash
        )
        self.veredas = mommy.make('fundo.fundo',
            nome='VEREDAS',
            administradora=btg_adm,
            gestora=anima,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(day=27,month=10,year=2014),
            pais=brasil,
            custodia=btg_cust,
            taxa_administracao=decimal.Decimal('0.06'),
            taxa_adm_minima=decimal.Decimal('3170'),
            capitalizacao_taxa_adm=fm.Fundo.CAPITALIZACAO[0][0],
            caixa_padrao=btg_cash
        )

        # Cotista
        cotista = mommy.make('fundo.Cotista',
            nome='ATENA',
            cota_media=decimal.Decimal(100)
        )

        # ATIVOS
        # Ação
        NATU = mommy.make('ativos.Acao',
            nome='NATU3',
            bbg_ticker='NATU3 BZ EQUITY',
            pais=brasil,
            moeda=real
        )
        MA = mommy.make('ativos.Acao',
            nome='MA',
            pais=eua,
            moeda=dolar
        )

        # Câmbio
        bmfxclco = mommy.make('ativos.Cambio',
            nome='BMFXCLCO',
            bbg_ticker='BMFXCLCO INDEX',
            moeda_origem=dolar,
            moeda_destino=real
        )

        # Fundos locais
        honor = mommy.make('ativos.Fundo_Local',
            nome='HONOR MASTER',
            bbg_ticker='HONMSTR BZ EQUITY',
            moeda=real,
            pais=brasil,
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=4),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
        )
        soberano = mommy.make('ativos.Fundo_Local',
            nome='SOBERANO',
            bbg_ticker='ITAUSOB BZ EQUITY',
            moeda=real,
            pais=brasil,
            data_cotizacao_resgate=datetime.timedelta(days=0),
            data_liquidacao_resgate=datetime.timedelta(days=0),
            data_cotizacao_aplicacao=datetime.timedelta(days=0),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
        )
        veredas = mommy.make('ativos.Fundo_Local',
            nome='VEREDAS FIA IE',
            bbg_ticker='FIMVRDS BZ EQUITY',
            moeda=real,
            pais=brasil,
            data_cotizacao_resgate=datetime.timedelta(days=1),
            data_liquidacao_resgate=datetime.timedelta(days=4),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.veredas
        )

        """
        Configuracao de cambio
        """

        configuration = mommy.make('configuracao.ConfigCambio',
            fundo=self.itatiaia,
        )
        configuration.cambio.add(bmfxclco)

        mommy.make('configuracao.ConfigZeragem',
            fundo=self.itatiaia,
            caixa=btg_cash,
            indice_zeragem=cdi
        )

        """
        Preços de mercado
        """
        self.data_carteira = datetime.date(day=23,month=3,year=2017)
        self.data_carteira_2 = datetime.date(day=24, month=3, year=2017)
        self.data_carteira_3 = datetime.date(day=27, month=3, year=2017)

        mommy.make('mercado.Preco',
            ativo=NATU,
            preco_fechamento=decimal.Decimal(28.10).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=decimal.Decimal(200).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(0.999754).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=soberano,
            preco_fechamento=decimal.Decimal(39.598808).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=honor,
            preco_fechamento=decimal.Decimal(21.232107).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=veredas,
            preco_fechamento=decimal.Decimal(1460.311401).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )
        mommy.make('mercado.Preco',
            ativo=bmfxclco,
            preco_fechamento=decimal.Decimal(3.1321).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira
        )

        mommy.make('mercado.Preco',
            ativo=NATU,
            preco_fechamento=decimal.Decimal(28.33).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=MA,
            preco_fechamento=decimal.Decimal(250).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(1.000).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=soberano,
            preco_fechamento=decimal.Decimal(39.616631).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=honor,
            preco_fechamento=decimal.Decimal(21.292116).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=veredas,
            preco_fechamento=decimal.Decimal(1480.665894).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )
        mommy.make('mercado.Preco',
            ativo=bmfxclco,
            preco_fechamento=decimal.Decimal(3.1096).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_2
        )

        mommy.make('mercado.Preco',
            ativo=NATU,
            preco_fechamento=decimal.Decimal(28.35).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_3
        )
        mommy.make('mercado.Preco',
            ativo=cdi,
            preco_fechamento=decimal.Decimal(1.000246).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_3
        )
        mommy.make('mercado.Preco',
            ativo=soberano,
            preco_fechamento=decimal.Decimal(39.634506).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_3
        )
        mommy.make('mercado.Preco',
            ativo=honor,
            preco_fechamento=decimal.Decimal(21.318707).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_3
        )
        mommy.make('mercado.Preco',
            ativo=veredas,
            preco_fechamento=decimal.Decimal(1487.9395163).quantize(decimal.Decimal('1.0000000')),
            data_referencia=self.data_carteira_3
        )
        mommy.make('mercado.Preco',
            ativo=bmfxclco,
            preco_fechamento=decimal.Decimal(3.1357).quantize(decimal.Decimal('1.000000')),
            data_referencia=self.data_carteira_3
        )

        """
        Boletas de ativos
        """
        # Boleta Aporte
        boleta_passivo = mommy.make('boletagem.BoletaPassivo',
            cotista=cotista,
            valor=decimal.Decimal(361096561.81).quantize(decimal.Decimal('1.00')),
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            fundo=self.itatiaia,
            cota=143.3045056,
        )

        boleta_NATU = mommy.make('boletagem.BoletaAcao',
            acao=NATU,
            data_operacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            custodia=itau_cust,
            corretora=bbdc_corr,
            operacao=bm.BoletaAcao.OPERACAO[0][0],
            fundo=self.itatiaia,
            quantidade=10320689,
            preco=decimal.Decimal(28.10).quantize(decimal.Decimal('1.00')),
            caixa_alvo=self.itatiaia.caixa_padrao
        )
        # boletaMA = mommy.make('boletagem.BoletaAcao',
        #     acao=MA,
        #     data_operacao=self.data_carteira,
        #     data_liquidacao=self.data_carteira_3,
        #     custodia=persh_cust,
        #     corretora=jeff_corr,
        #     operacao=bm.BoletaAcao.OPERACAO[0][0],
        #     fundo=self.itatiaia,
        #     quantidade=10320689,
        #     preco=decimal.Decimal(200).quantize(decimal.Decimal('1.00')),
        #     caixa_alvo=jeff_cash
        # )

        # Boletas Fundos locais
        boleta_Honor = mommy.make('boletagem.BoletaFundoLocal',
            ativo=honor,
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            fundo=self.itatiaia,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            liquidacao=bm.BoletaFundoLocal.TIPO_LIQUIDACAO[1][0],
            financeiro=decimal.Decimal(41932947.71).quantize(decimal.Decimal('1.00')),
            quantidade=decimal.Decimal(1974978.15498).quantize(decimal.Decimal('1.00000')),
            preco=decimal.Decimal(21.2321071).quantize(decimal.Decimal('1.000000')),
            caixa_alvo=self.itatiaia.caixa_padrao,
            custodia=itau_cust
        )
        boleta_Soberano = mommy.make('boletagem.BoletaFundoLocal',
            ativo=soberano,
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            fundo=self.itatiaia,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            liquidacao=bm.BoletaFundoLocal.TIPO_LIQUIDACAO[1][0],
            financeiro=decimal.Decimal(1947954.29).quantize(decimal.Decimal('1.00')),
            quantidade=decimal.Decimal(49192.2444).quantize(decimal.Decimal('1.000000')),
            preco=decimal.Decimal(39.498809).quantize(decimal.Decimal('1.000000')),
            caixa_alvo=self.itatiaia.caixa_padrao,
            custodia=itau_cust
        )
        boleta_Veredas = mommy.make('boletagem.BoletaFundoLocal',
            ativo=veredas,
            data_operacao=self.data_carteira,
            data_cotizacao=self.data_carteira,
            data_liquidacao=self.data_carteira,
            fundo=self.itatiaia,
            operacao=bm.BoletaFundoLocal.OPERACAO[0][0],
            liquidacao=bm.BoletaFundoLocal.TIPO_LIQUIDACAO[0][0],
            financeiro=decimal.Decimal(27192831.71).quantize(decimal.Decimal('1.00')),
            quantidade=decimal.Decimal(18621.2562).quantize(decimal.Decimal('1.000000')),
            preco=decimal.Decimal(1460.3113).quantize(decimal.Decimal('1.000000')),
            caixa_alvo=self.itatiaia.caixa_padrao,
            custodia=itau_cust
        )

        boleta_CPR_Audit = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa Auditoria 03.2017 - DIARIZAÇÃO",
            fundo=self.itatiaia,
            valor_parcial=decimal.Decimal(-7.24).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=23, month=3, year=2017),
            data_vigencia_inicio=datetime.date(day=23, month=3, year=2017),
            data_vigencia_fim=datetime.date(day=23, month=3, year=2018),
            data_pagamento=datetime.date(day=23, month=3, year=2018),
            tipo=bm.BoletaCPR.TIPO[0][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )

        boleta_CPR_Gestao = mommy.make('boletagem.BoletaCPR',
            descricao="Despesa Gestão 03.2017 - DIARIZAÇÃO",
            fundo=self.itatiaia,
            valor_parcial=decimal.Decimal(-1956.52).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=23, month=3, year=2017),
            data_vigencia_inicio=datetime.date(day=23, month=3, year=2017),
            data_vigencia_fim=datetime.date(day=31, month=3, year=2018),
            data_pagamento=datetime.date(day=31, month=3, year=2018),
            tipo=bm.BoletaCPR.TIPO[0][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )

        boleta_CPR_Administracao = mommy.make('boletagem.BoletaCPR',
            descricao="Taxa de Administração 03.2017",
            fundo=self.itatiaia,
            valor_cheio=decimal.Decimal('-0').quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=1, month=3, year=2017),
            data_vigencia_inicio=datetime.date(day=1, month=3, year=2017),
            data_vigencia_fim=datetime.date(day=31, month=3, year=2017),
            data_pagamento=datetime.date(day=7, month=4, year=2017),
            tipo=bm.BoletaCPR.TIPO[4][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[0][0]
        )

        vertice_taxa_adm = mommy.make('fundo.Vertice',
            fundo=self.itatiaia,
            custodia=btg_cust,
            corretora=btg_corr,
            quantidade=1,
            valor=decimal.Decimal('0'),
            preco=1,
            movimentacao=0,
            data=datetime.date(day=22, month=3, year=2017),
            cambio=1    ,
            content_object=boleta_CPR_Administracao
        )
        vertice_veredas = mommy.make('fundo.Vertice',
            fundo=self.itatiaia,
            custodia=btg_cust,
            corretora=btg_corr,
            quantidade=18621.25616,
            valor=decimal.Decimal('26934499.11'),
            preco=decimal.Decimal('1446.438354'),
            movimentacao=0,
            data=datetime.date(day=22, month=3, year=2017),
            cambio=1,
            content_object=veredas
        )

        carteira = mommy.make('fundo.carteira',
            fundo=self.itatiaia,
            data=datetime.date(day=22, month=3, year=2017),
            cota=decimal.Decimal('141.033726'),
            pl=decimal.Decimal('355374684.96'),
            movimentacao=0
        )
        carteira.vertices.add(vertice_taxa_adm)
        carteira.vertices.add(vertice_veredas)

        boleta_CPR_JCP_NATU3 = mommy.make('boletagem.BoletaCPR',
            descricao="JCP NATU3",
            fundo=self.itatiaia,
            valor_cheio=decimal.Decimal(134323.77).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=1, month=3, year=2017),
            data_pagamento=datetime.date(day=20, month=4, year=2017),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_JCP_NATU3 = mommy.make('boletagem.BoletaProvisao',
            descricao="JCP NATU3",
            fundo=self.itatiaia,
            caixa_alvo=self.itatiaia.caixa_padrao,
            data_pagamento=boleta_CPR_JCP_NATU3.data_pagamento,
            financeiro=boleta_CPR_JCP_NATU3.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )

        boleta_CPR_DVD_NATU3 = mommy.make('boletagem.BoletaCPR',
            descricao="Dividendos NATU3",
            fundo=self.itatiaia,
            valor_cheio=decimal.Decimal(1229823.62).quantize(decimal.Decimal('1.00')),
            data_inicio=datetime.date(day=1, month=3, year=2017),
            data_pagamento=datetime.date(day=20, month=4, year=2017),
            tipo=bm.BoletaCPR.TIPO[2][0],
            capitalizacao=bm.BoletaCPR.CAPITALIZACAO[2][0]
        )
        boleta_provisao_DVD_NATU3 = mommy.make('boletagem.BoletaProvisao',
            descricao="Dividendos NATU3",
            fundo=self.itatiaia,
            caixa_alvo=self.itatiaia.caixa_padrao,
            data_pagamento=boleta_CPR_DVD_NATU3.data_pagamento,
            financeiro=boleta_CPR_DVD_NATU3.valor_cheio,
            estado=bm.BoletaProvisao.ESTADO[0][1]
        )
        import mercado.models as mm
        provento_natu3 = mommy.make('mercado.Provento',
            ativo=MA,
            data_com=self.data_carteira,
            data_ex=self.data_carteira_2,
            data_pagamento=self.data_carteira_3,
            tipo_provento=mm.Provento.TIPO[0][0],
            valor_liquido=0.15,
        )



    def test_fechamento(self):
        pass
        # self.itatiaia.zeragem_de_caixa(self.data_carteira)
        # self.itatiaia.verificar_proventos(self.data_carteira)
        # self.itatiaia.fechar_boletas_do_fundo(self.data_carteira)
        # self.itatiaia.criar_vertices(self.data_carteira)
        # self.itatiaia.consolidar_vertices(self.data_carteira)
        # self.itatiaia.calcular_cota(self.data_carteira)
        #
        # self.itatiaia.zeragem_de_caixa(self.data_carteira_2)
        # self.itatiaia.verificar_proventos(self.data_carteira_2)
        # self.itatiaia.fechar_boletas_do_fundo(self.data_carteira_2)
        # self.itatiaia.criar_vertices(self.data_carteira_2)
        # self.itatiaia.consolidar_vertices(self.data_carteira_2)
        # self.itatiaia.calcular_cota(self.data_carteira_2)
        #
        # self.itatiaia.zeragem_de_caixa(self.data_carteira_3)
        # self.itatiaia.verificar_proventos(self.data_carteira_3)
        # self.itatiaia.fechar_boletas_do_fundo(self.data_carteira_3)
        # self.itatiaia.criar_vertices(self.data_carteira_3)
        # self.itatiaia.consolidar_vertices(self.data_carteira_3)
        # self.itatiaia.calcular_cota(self.data_carteira_3)
