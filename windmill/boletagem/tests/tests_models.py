import datetime
import decimal
from model_mommy import mommy
from django.test import TestCase
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
import boletagem.models as bm
import fundo.models as fm

# Create your tests here.
class BoletaEmprestimoUnitTests(TestCase):

    def setUp(self):
        # Boleta inicial - usada para testar os métodos unitários
        # Boleta em aberto - sem data de liquidacao
        self.boleta = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao='2018-10-02',
            data_reversao='2018-10-03',
            reversivel=True,
            quantidade=10000,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15))
        # Boleta para ser testar liquidaçaõ completa
        self.boleta_liquidada = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao='2018-10-01',
            data_liquidacao='2018-10-31',
            quantidade=10000,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15))
        self.boleta_renovada_completa = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao='2018-10-01',
            data_vencimento='2018-10-31',
            data_reversao='2018-10-02',
            quantidade=10000,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15))
        self.boleta_renovada_parcial = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao='2018-10-01',
            data_vencimento='2018-10-31',
            quantidade=1000,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15))
        self.boleta_a_liquidar_completo = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_reversao=datetime.date(year=2018, month=10, day=2),
            data_vencimento=datetime.date(year=2018, month=11, day=30),
            quantidade=10000,
            reversivel=True,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15))
        self.boleta_a_liquidar_parcial = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_reversao=datetime.date(year=2018, month=10, day=2),
            data_vencimento=datetime.date(year=2018, month=11, day=30),
            quantidade=15000,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15),
            reversivel=True)
        self.data_de_liquidacao = datetime.date(year=2018, month=10, day=30)
        self.quantidade_liquidada = 10000

    def test_boleta_emprestimo_criada(self):
        self.assertIsInstance(self.boleta, bm.BoletaEmprestimo)

    def test_criar_provisao(self):
        """
        Testa se a boleta de empréstimo cria a provisão corretamente. A boleta
        deve criar uma provisão apenas quando ela está liquidada.
        """
        # Verifica se a boleta não possui uma boleta de provisão ligada.
        self.assertFalse(self.boleta_liquidada.boleta_provisao.all().exists())
        self.boleta_liquidada.criar_boleta_provisao()
        # Verifica se a criação da boleta de provisão ligou a boleta de
        # empréstimo à boleta de provisão.
        self.assertTrue(self.boleta_liquidada.boleta_provisao.all().exists())
        # Buscando a boleta de provisão criada.
        type = ContentType.objects.get_for_model(self.boleta_liquidada)
        prov = bm.BoletaProvisao.objects.get(content_type__pk=type.id, object_id=self.boleta_liquidada.id)
        # Verifica se a provisão é uma boleta de provisão mesmo.
        self.assertIsInstance(prov, bm.BoletaProvisao)
        # Verifica informações da boleta de provisão.
        self.assertEqual(prov.financeiro, self.boleta_liquidada.financeiro())
        self.assertEqual(prov.caixa_alvo, self.boleta_liquidada.caixa_alvo)
        self.assertEqual(prov.data_pagamento, self.boleta_liquidada.calendario.dia_trabalho(self.boleta_liquidada.data_liquidacao, 1))
        self.assertEqual(prov.fundo, self.boleta_liquidada.fundo)

    def test_boleta_original_auto_referencia(self):
        self.assertEqual(self.boleta.id, self.boleta.boleta_original.id )

    def test_checar_conta_financeiro_boleta_aberta(self):
        """
        Testa se a conta do financeiro está ok para uma boleta em aberto,
        ou seja, sem data de liquidacao
        """
        data_ref = datetime.date.today()
        financeiro = round(self.boleta.preco * self.boleta.quantidade * \
        ((1 + self.boleta.taxa/100) ** decimal.Decimal((self.boleta.calendario.dia_trabalho_total(self.boleta.data_operacao, data_ref)/252))-1),2)
        # Deve haver uma movimentação relacionada à boleta
        self.assertEqual(financeiro, self.boleta.financeiro())

    def test_checar_conta_financeiro_boleta_liquidada(self):
        """
        Testa se a conta do financeiro está correta para boletas liquidadas
        """
        financeiro = round(self.boleta_liquidada.preco * self.boleta_liquidada.quantidade * \
        ((1 + self.boleta_liquidada.taxa/100) ** decimal.Decimal((self.boleta_liquidada.calendario.dia_trabalho_total(self.boleta_liquidada.data_operacao, self.boleta_liquidada.data_liquidacao)/252))-1),2)
        self.assertEqual(financeiro, self.boleta_liquidada.financeiro())

    def test_criar_movimentacao_boleta_liquidada(self):
        """
        Testa se a função de criação de movimentação cria uma movimentação para
        uma boleta liquidada (com data de liquidação).
        """
        # Primeiro, não deve haver nenhuma movimentação já ligada à boleta
        self.assertFalse(self.boleta_liquidada.relacao_movimentacao.all().exists())
        self.boleta_liquidada.criar_movimentacao()
        # Agora há uma movimentação ligada.
        self.assertTrue(self.boleta_liquidada.relacao_movimentacao.all().exists())
        type = ContentType.objects.get_for_model(self.boleta_liquidada)
        movs = fm.Movimentacao.objects.get(content_type__pk=type.id, object_id=self.boleta_liquidada.id)
        # Encontra a movimentação ligada à boleta
        self.assertIsInstance(movs, fm.Movimentacao)
        # As características da boleta devem bater com a movimentação
        self.assertEqual(movs.valor, -self.boleta_liquidada.financeiro())
        self.assertEqual(movs.fundo, self.boleta_liquidada.fundo)
        self.assertEqual(movs.data, self.boleta_liquidada.calendario.dia_trabalho(self.boleta_liquidada.data_liquidacao, 1))
        print(movs.objeto_movimentacao)
        print(self.boleta_liquidada.ativo)
        self.assertEqual(movs.objeto_movimentacao, self.boleta_liquidada.ativo)

    def test_falha_criar_movimentacao_sem_liquidar(self):
        """
        Testa se a exceção ao tentar criar uma movimentação de uma boleta
        não liquidada é levantada
        """
        self.assertRaises(TypeError, self.boleta.criar_movimentacao)

    def test_renovar_completo(self):
        """
        Testa se o contrato é renovado completamente
        """
        nova_data_vencimento = '2018-11-30'
        data_renovacao = '2018-10-20'
        self.boleta_renovada_completa.renovar_boleta(data_vencimento=nova_data_vencimento,
            quantidade=self.boleta_renovada_completa.quantidade, data_renovacao=data_renovacao)
        self.assertEqual(self.boleta_renovada_completa.data_vencimento, nova_data_vencimento)

    def test_renovar_parcial(self):
        """
        Caso uma boleta seja renovada parcialmente, a parcela não renovada
        deve ser liquidada.
        A parcela renovada deve possuir a quantidade renovada e o novo
        vencimento.
        """
        nova_data_vencimento = '2018-11-30'
        quantidade_renovada = 300
        data_renovacao = '2018-10-20'
        # A boleta original é renovada. A parcela liquidada forma uma nova
        # boleta já liquidada, com parametro boleta_original apontando para a boleta
        # original
        self.boleta_renovada_parcial.renovar_boleta(data_vencimento=nova_data_vencimento,
            quantidade=quantidade_renovada,
            data_renovacao=data_renovacao)
        """
        Verificando a parcela liquidada.
        """
        # Buscando a boleta liquidada
        boleta_liquidada = bm.BoletaEmprestimo.objects.get(boleta_original=self.boleta_renovada_parcial,
            data_liquidacao=data_renovacao)
        # Checa se a boleta renovada renovou sua data de vencimento
        self.assertEqual(self.boleta_renovada_parcial.data_vencimento, nova_data_vencimento)
        # Checa se a quantidade da boleta renovada bate
        self.assertEqual(self.boleta_renovada_parcial.quantidade, quantidade_renovada)
        # Checa se a boleta liquidada possui a quantidade certa
        self.assertEqual(boleta_liquidada.quantidade, quantidade_renovada)
        # Checa se a boleta liquidada foi liquidada na data correta
        self.assertEqual(boleta_liquidada.data_liquidacao, datetime.datetime.strptime(data_renovacao, '%Y-%m-%d').date())
        # Checa se a data de inicio dos contratos batem
        self.assertEqual(datetime.datetime.strptime(self.boleta_renovada_parcial.data_operacao, '%Y-%m-%d').date(), boleta_liquidada.data_operacao)
        # Checa se os preços da parcela liquidada e da original batem
        self.assertEqual(self.boleta_renovada_parcial.preco, boleta_liquidada.preco)
        # Checa se a taxa de aluguel da parcela liquidada bate com a original
        self.assertEqual(round(self.boleta_renovada_parcial.taxa,6), round(boleta_liquidada.taxa, 6))

        """
        Verificando a parcela renovada.
        """
        # Checando se a quantidade foi atualizada corretamente
        self.assertEqual(self.boleta_renovada_parcial.quantidade, quantidade_renovada)
        # Checando se a data de vencimento foi atualizada
        self.assertEqual(self.boleta_renovada_parcial.data_vencimento, nova_data_vencimento)

    def test_liquidar_boleta_completo(self):
        """
        Ao liquidar uma boleta, devem ser gerados uma movimentação do ativo
        e uma boleta de provisão para a movimentação do caixa, além da
        atualização da boleta com a data de liquidação.
        """
        # Chamando função de liquidação da boleta
        self.boleta_a_liquidar_completo.liquidar_boleta(quantidade=self.quantidade_liquidada,
            data_referencia=self.data_de_liquidacao)
        # Conferindo a data de liquidação da boleta liquidada
        self.assertEqual(self.boleta_a_liquidar_completo.data_liquidacao, self.data_de_liquidacao)
        # Pegando a movimentação criada.
        type = ContentType.objects.get_for_model(self.boleta_a_liquidar_completo)
        movs = fm.Movimentacao.objects.get(content_type__pk=type.id, object_id=self.boleta_a_liquidar_completo.id)
        # Verifica se a movimentação criada existe. As informações da criação
        # já foram verificadas em testes anteriores
        self.assertIsInstance(movs, fm.Movimentacao)

        # Conferindo se a criação da provisão foi feita.
        bol_prov = bm.BoletaProvisao.objects.get(content_type__pk=type.id, object_id=self.boleta_a_liquidar_completo.id)
        self.assertIsInstance(bol_prov, bm.BoletaProvisao)
        # Conferindo informações da boleta de provisão
        self.assertEqual(bol_prov.financeiro, self.boleta_a_liquidar_completo.financeiro())
        self.assertEqual(bol_prov.caixa_alvo, self.boleta_a_liquidar_completo.caixa_alvo)
        self.assertEqual(bol_prov.fundo, self.boleta_a_liquidar_completo.fundo)
        self.assertEqual(bol_prov.data_pagamento, self.boleta_a_liquidar_completo.calendario.dia_trabalho(self.boleta_a_liquidar_completo.data_liquidacao, 1))

    def test_liquidar_parcial(self):
        """
        Ao liquidar uma boleta parcialmente, deve ser gerado uma movimentação
        do ativo no valor do equivalente à parcela da quantidade liquidada,
        uma provisão com mesmo valor financeiro à marcada na movimentação do
        ativo.
        """
        quantidade_original = self.boleta_a_liquidar_parcial.quantidade
        # Liquidação de boleta
        self.boleta_a_liquidar_parcial.liquidar_boleta(quantidade=self.quantidade_liquidada,
            data_referencia=self.data_de_liquidacao)
        # Buscando a boleta parcialmente liquidada
        boleta_liquidada = bm.BoletaEmprestimo.objects.get(data_liquidacao=self.data_de_liquidacao,
            quantidade=self.quantidade_liquidada)
        # A boleta original deve ter sua quantidade atualizada com a
        # quantidade que ainda está alugada
        self.assertEqual(self.boleta_a_liquidar_parcial.quantidade,
            quantidade_original - self.quantidade_liquidada)
        # Verificar se a boleta liquidada possui as características da boleta
        # original, com a quantidade liquidada
        self.assertEqual(boleta_liquidada.quantidade, self.quantidade_liquidada)
        self.assertEqual(boleta_liquidada.data_liquidacao, self.data_de_liquidacao)
        self.assertEqual(boleta_liquidada.ativo, self.boleta_a_liquidar_parcial.ativo)
        self.assertEqual(boleta_liquidada.data_operacao, self.boleta_a_liquidar_parcial.data_operacao)
        self.assertEqual(boleta_liquidada.fundo, self.boleta_a_liquidar_parcial.fundo)
        self.assertEqual(boleta_liquidada.corretora, self.boleta_a_liquidar_parcial.corretora)
        self.assertEqual(boleta_liquidada.data_vencimento, self.boleta_a_liquidar_parcial.data_vencimento)
        self.assertEqual(boleta_liquidada.reversivel, self.boleta_a_liquidar_parcial.reversivel)
        self.assertEqual(boleta_liquidada.data_reversao, self.boleta_a_liquidar_parcial.data_reversao)
        self.assertEqual(boleta_liquidada.operacao, self.boleta_a_liquidar_parcial.operacao)
        self.assertEqual(boleta_liquidada.comissao, self.boleta_a_liquidar_parcial.comissao)
        self.assertEqual(round(boleta_liquidada.taxa,6), round(self.boleta_a_liquidar_parcial.taxa,6))
        self.assertEqual(boleta_liquidada.preco, self.boleta_a_liquidar_parcial.preco)
        self.assertEqual(boleta_liquidada.boleta_original.id, self.boleta_a_liquidar_parcial.boleta_original.id)
        self.assertEqual(boleta_liquidada.caixa_alvo, self.boleta_a_liquidar_parcial.caixa_alvo)
        self.assertEqual(boleta_liquidada.calendario, self.boleta_a_liquidar_parcial.calendario)
        # Verificar se a boleta liquidada gerou a movimentação
        type = ContentType.objects.get_for_model(boleta_liquidada)
        movs = fm.Movimentacao.objects.get(content_type__pk=type.id, object_id=boleta_liquidada.id)
        # Verificar se a boleta liquidada gerou a boleta de provisão
        bol_prov = bm.BoletaProvisao.objects.get(content_type__pk=type.id, object_id=boleta_liquidada.id)
