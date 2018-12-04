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
        dolar = mommy.make('ativos.Moeda',
            nome='Dólar',
            codigo='USD'
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
            moeda=moeda,
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
            nome='fundo_local_gerido',
            gestora=gestora,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            caixa_padrao=caixa_padrao,
            custodia=custodia
        )
        # Fundo não gerido
        self.fundo_qualquer = mommy.make("fundo.Fundo",
            nome='fundo_local_nao_gerido',
            gestora=gestora_qualquer,
            categoria=fm.Fundo.CATEGORIAS[0][0],
            data_de_inicio=datetime.date(year=2017, month=10, day=27),
            caixa_padrao=caixa_padrao
        )
        # Fundo Anima Master, gerido, que investe em outros fundos geridos
        self.fundo_master = mommy.make("fundo.Fundo",
            nome='fundo_local_master',
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
        fundo_off_nao_gerido = mommy.make('ativos.Fundo_Offshore',
            nome='fundo_off_nao_gerido',
            data_cotizacao_resgate=datetime.timedelta(days=4),
            data_liquidacao_resgate=datetime.timedelta(days=5),
            data_cotizacao_aplicacao=datetime.timedelta(days=1),
            data_liquidacao_aplicacao=datetime.timedelta(days=0),
            gestao=self.fundo_qualquer
        )

        """
        Setup de preços
        """
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
            ativo=fundo_off_nao_gerido,
            preco_fechamento=1000,
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
            ativo=fundo_off_nao_gerido,
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
            fundo=self.fundo
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

    def test_juntar_quantidades(self):
        self.fundo.fechar_boletas_do_fundo(self.data_fechamento)
        self.fundo.criar_vertices(self.data_fechamento)

        self.fundo.fechar_boletas_do_fundo(self.data_carteira)
        self.fundo.criar_vertices(self.data_carteira)

        self.fundo.fechar_boletas_do_fundo(self.data_carteira1)
        self.fundo.criar_vertices(self.data_carteira1)

        # self.fundo.fechar_boletas_do_fundo(self.data_carteira2)
        # self.fundo.criar_vertices(self.data_carteira2)
        #
        # self.fundo.fechar_boletas_do_fundo(self.data_carteira3)
        # self.fundo.criar_vertices(self.data_carteira3)

        self.assertTrue(False)
        self.assertTrue(fm.Vertice.objects.filter(fundo=self.fundo, data=self.data_carteira).exists())
