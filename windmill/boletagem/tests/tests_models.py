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

# Create your tests here.
class BoletaEmprestimoUnitTests(TestCase):
    """
    Classe de testes para o modelo BoletaEmprestimo.
    """

    def setUp(self):
        # Boleta inicial - usada para testar os métodos unitários
        # Boleta em aberto - sem data de liquidacao
        self.boleta = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=2),
            data_reversao=datetime.date(year=2018, month=10, day=3),
            reversivel=True,
            quantidade=10000,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )
        self.boleta.full_clean()
        self.boleta.save()
        # Boleta para ser testar liquidaçaõ completa
        self.boleta_liquidada = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_liquidacao=datetime.date(year=2018, month=10, day=31),
            quantidade=10000,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )
        self.boleta_liquidada.full_clean()
        self.boleta_liquidada.save()
        self.boleta_renovada_completa = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_vencimento=datetime.date(year=2018, month=10, day=31),
            data_reversao=datetime.date(year=2018, month=10, day=2),
            quantidade=10000,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )
        self.boleta_renovada_completa.full_clean()
        self.boleta_renovada_completa.save()
        self.boleta_renovada_parcial = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_vencimento=datetime.date(year=2018, month=10, day=24),
            quantidade=1000,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )
        self.boleta_renovada_parcial.full_clean()
        self.boleta_renovada_parcial.save()
        self.boleta_a_liquidar_completo = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_reversao=datetime.date(year=2018, month=10, day=2),
            data_vencimento=datetime.date(year=2018, month=11, day=30),
            quantidade=10000,
            reversivel=True,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000'))
        )
        self.boleta_a_liquidar_completo.full_clean()
        self.boleta_a_liquidar_completo.save()
        self.boleta_a_liquidar_parcial = mommy.make('boletagem.BoletaEmprestimo',
            data_operacao=datetime.date(year=2018, month=10, day=1),
            data_reversao=datetime.date(year=2018, month=10, day=5),
            data_vencimento=datetime.date(year=2018, month=12, day=25),
            quantidade=15000,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.15).quantize(decimal.Decimal('1.000000')),
            reversivel=True)
        self.boleta_a_liquidar_parcial.full_clean()
        self.boleta_a_liquidar_parcial.save()
        self.boleta_vencimento_errado = mommy.make('boletagem.BoletaEmprestimo',
            data_vencimento=datetime.date(year=2018, month=10, day=1),
            data_operacao=datetime.date(year=2018, month=10, day=3))
        self.boleta_vencimento_errado.full_clean()
        self.boleta_vencimento_errado.save()
        self.boleta_liquidacao_anterior_operacao = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=1),
            data_operacao=datetime.date(year=2018, month=10, day=3),
            data_vencimento=datetime.date(year=2018, month=10, day=24))
        self.boleta_liquidacao_anterior_operacao.full_clean()
        self.boleta_liquidacao_anterior_operacao.save()
        self.boleta_liquidacao_posterior_vencimento = mommy.make('boletagem.BoletaEmprestimo',
            data_vencimento=datetime.date(year=2018, month=10, day=1),
            data_liquidacao=datetime.date(year=2018, month=10, day=13))
        self.boleta_liquidacao_posterior_vencimento.full_clean()
        self.boleta_liquidacao_posterior_vencimento.save()
        self.boleta_liquidacao_anterior_reversivel = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=1),
            data_reversao=datetime.date(year=2018, month=10, day=3),
            data_vencimento=datetime.date(year=2018, month=10, day=20))
        self.boleta_liquidacao_anterior_reversivel.full_clean()
        self.boleta_liquidacao_anterior_reversivel.save()
        self.boleta_correta = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=25),
            reversivel=False,
            data_vencimento=datetime.date(year=2018, month=10, day=30),
            data_operacao=datetime.date(year=2018, month=10, day=1),
            quantidade=decimal.Decimal(1000).quantize(decimal.Decimal('1.000000')),
            taxa=decimal.Decimal(0.2).quantize(decimal.Decimal('1.000000')),
            preco=10)
        self.boleta_correta.full_clean()
        self.boleta_correta.save()
        self.data_de_liquidacao = datetime.date(year=2018, month=10, day=30)
        self.quantidade_liquidada = 10000

    def test_vencimento_invalido(self):
        self.assertRaises(ValidationError, self.boleta_vencimento_errado.clean_data_vencimento)

    def test_liquidacao_invalida(self):
        self.assertRaises(ValidationError, self.boleta_liquidacao_anterior_operacao.clean_data_liquidacao)
        self.assertRaises(ValidationError, self.boleta_liquidacao_posterior_vencimento.clean_data_liquidacao)
        self.assertRaises(ValidationError, self.boleta_liquidacao_anterior_reversivel.clean_data_liquidacao)

    def test_data_reversao_invalida(self):
        """
        Testa a validação da data de reversão do contrato de aluguel.
        """
        boleta_reversao_antecipada = mommy.make('boletagem.BoletaEmprestimo',
            reversivel=True,
            data_operacao=datetime.date(year=2018, month=10, day=3),
            data_reversao=datetime.date(year=2018, month=10, day=2))
        boleta_reversao_vazia = mommy.make('boletagem.BoletaEmprestimo',
            reversivel=True,
            data_operacao=datetime.date(year=2018, month=10, day=3))
        self.assertRaises(ValidationError, boleta_reversao_antecipada.clean_data_reversao)
        self.assertRaises(ValueError, boleta_reversao_vazia.clean_data_reversao)

    # Implementar verificação de quantidade deve ser igual ou menor que a quantidade disponível.
    @pytest.mark.xfail
    def test_quantidade_invalida(self):
        """
        Teste validação quantidade
        """
        boleta_quantidade_invalida = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=25),
            reversivel=False,
            data_vencimento=datetime.date(year=2018, month=10, day=30),
            data_operacao=datetime.date(year=2018, month=10, day=1),
            quantidade=-1)
        self.assertRaises(ValidationError, boleta_quantidade_invalida.clean_quantidade)
        self.assertRaises(ValueError, boleta_quantidade_superior_que_disponivel.clean_quantidade)

    def test_taxa_invalida(self):
        """
        Teste de validação do campo taxa
        """
        boleta_taxa_invalida = self.boleta_correta
        boleta_taxa_invalida.id = None
        boleta_taxa_invalida.taxa = -0.1
        self.assertRaises(ValidationError, boleta_taxa_invalida.clean_taxa)

    def test_preco_invalido(self):
        """
        Teste de validação do campo preço
        """
        boleta_preco_invalido = self.boleta_correta
        boleta_preco_invalido.id = None
        boleta_preco_invalido.preco = -10
        self.assertRaises(ValidationError, boleta_preco_invalido.clean_preco)

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
        nova_data_vencimento = datetime.date(year=2018, month=11, day=30)
        data_renovacao = datetime.date(year=2018, month=10, day=20)
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
        nova_data_vencimento = datetime.date(year=2018, month=11, day=30)
        quantidade_renovada = 300
        data_renovacao = datetime.date(year=2018, month=10, day=20)
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
        self.assertEqual(boleta_liquidada.data_liquidacao, data_renovacao)
        # Checa se a data de inicio dos contratos batem
        self.assertEqual(self.boleta_renovada_parcial.data_operacao, boleta_liquidada.data_operacao)
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

    @pytest.mark.xfail
    def test_fechar_boleta(self):
        """
        Testar fechamento de boleta de empréstimo
        """
        self.assertRaises(ValidationError, self.boleta.fechar_boleta)

class BoletaAcaoUnitTests(TestCase):
    """
    Classe de testes para o modelo BoletaAcao.
    """
    def setUp(self):
        self.boleta = mommy.make('boletagem.BoletaAcao',
            data_operacao=datetime.date(year=2018, month=10, day=2),
            data_liquidacao=datetime.date(year=2018, month=10, day=5),
            operacao='C',
            quantidade=100,
            preco=decimal.Decimal(10).quantize(decimal.Decimal('1.0000000'))
        )
        self.boleta.full_clean()
        self.boleta.save()

    def test_liquidacao_invalida(self):
        """
        Testa a validação do campo data_liquidação da boleta de ações
        """
        self.boleta.id = None
        self.boleta.data_liquidacao = self.boleta.data_operacao - datetime.timedelta(days=2)
        self.assertRaises(ValidationError, self.boleta.clean_data_liquidacao)

    def test_operacao_quantidade_alinhados(self):
        """
        Testa a validação do campo quantidade.
        """
        boleta_copia = self.boleta
        boleta_copia.id = None
        boleta_copia.operacao = 'V'
        boleta_copia.quantidade = 1000
        boleta_copia.clean_quantidade()
        self.assertEqual(-1000, boleta_copia.quantidade)
        self.assertEqual('V', boleta_copia.operacao)
        boleta_copia.operacao = 'C'
        boleta_copia.quantidade = -1000
        boleta_copia.clean_quantidade()
        self.assertEqual(1000, boleta_copia.quantidade)
        self.assertEqual('C', boleta_copia.operacao)

    def test_clean_preco(self):
        copia = self.boleta
        copia.id = None
        preco_negativo = -10
        copia.preco = preco_negativo
        copia.clean_preco()
        self.assertEqual(copia.preco, -preco_negativo)

    def test_criar_movimentacao(self):
        """
        Testa se a função de criação de movimentação cria uma movimentação para
        uma boleta.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        # Primeiro, não deve haver nenhuma movimentação já ligada à boleta
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.criar_movimentacao()
        # Agora há uma movimentação ligada.
        self.assertTrue(copia.relacao_movimentacao.all().exists())
        type = ContentType.objects.get_for_model(copia)
        movs = fm.Movimentacao.objects.get(content_type__pk=type.id, object_id=copia.id)
        # Encontra a movimentação ligada à boleta
        self.assertIsInstance(movs, fm.Movimentacao)
        # As características da boleta devem bater com a movimentação
        self.assertEqual(movs.valor, copia.preco * copia.quantidade + copia.corretagem)
        self.assertEqual(movs.fundo, copia.fundo)
        # Data de movimentação do ativo casa com a data de operação
        self.assertEqual(movs.data, copia.data_operacao)
        self.assertEqual(movs.objeto_movimentacao, copia.acao)

    def test_criar_quantidade(self):
        """
        Testa se a função de criação de quantidade cria uma quantidade para
        uma boleta.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        # Primeiro, não deve haver nenhuma movimentação já ligada à boleta
        self.assertFalse(copia.relacao_quantidade.all().exists())
        copia.criar_quantidade()
        # Agora há uma movimentação ligada.
        self.assertTrue(copia.relacao_quantidade.all().exists())
        type = ContentType.objects.get_for_model(copia)
        qtd = fm.Quantidade.objects.get(content_type__pk=type.id, object_id=copia.id)
        # Encontra a movimentação ligada à boleta
        self.assertIsInstance(qtd, fm.Quantidade)
        # As características da boleta devem bater com a movimentação
        self.assertEqual(qtd.qtd, copia.quantidade)
        self.assertEqual(qtd.fundo, copia.fundo)
        # Data de movimentação do ativo casa com a data de operação
        self.assertEqual(qtd.data, copia.data_operacao)
        self.assertEqual(qtd.objeto_quantidade, copia.acao)

    def test_criar_boleta_CPR(self):
        """
        Testa a criação de uma boleta de CPR ligada à boleta de Ação
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        # Primeiro, não deve haver nenhuma movimentação já ligada à boleta
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        # Agora há uma movimentação ligada.
        self.assertTrue(copia.boleta_CPR.all().exists())
        type = ContentType.objects.get_for_model(copia)
        CPR = bm.BoletaCPR.objects.get(content_type__pk=type.id, object_id=copia.id)
        # Encontra a movimentação ligada à boleta
        self.assertIsInstance(CPR, bm.BoletaCPR)
        # As características da boleta devem bater com a movimentação
        self.assertEqual(CPR.valor_cheio, - copia.quantidade*copia.preco + copia.corretagem)
        self.assertEqual(CPR.data_inicio, copia.data_operacao)
        self.assertEqual(CPR.data_pagamento, copia.data_liquidacao)
        self.assertEqual(CPR.fundo, copia.fundo)
        self.assertEqual(CPR.content_object, copia)

    def test_criar_provisao(self):
        """
        Testa se a boleta de provisão é criada.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        # Primeiro, não deve haver nenhuma movimentação já ligada à boleta
        self.assertFalse(copia.boleta_provisao.all().exists())
        copia.criar_boleta_provisao()
        # Agora há uma movimentação ligada.
        self.assertTrue(copia.boleta_provisao.all().exists())
        type = ContentType.objects.get_for_model(copia)
        provisao = bm.BoletaProvisao.objects.get(content_type__pk=type.id, object_id=copia.id)
        # Encontra a movimentação ligada à boleta
        self.assertIsInstance(provisao, bm.BoletaProvisao)
        # As características da boleta devem bater com a movimentação
        self.assertEqual(provisao.caixa_alvo, copia.caixa_alvo)
        self.assertEqual(provisao.financeiro, - (copia.quantidade*copia.preco) + copia.corretagem)
        self.assertEqual(provisao.data_pagamento, copia.data_liquidacao)
        self.assertEqual(provisao.fundo, copia.fundo)
        self.assertEqual(provisao.content_object, copia)

    def test_fechar_boleta(self):
        """
        Testa se o fechamento da boleta gera todas os objetos necessários.
        """
        copia = self.boleta
        copia.id = None
        copia.full_clean()
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        self.assertFalse(copia.boleta_CPR.all().exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.fechar_boleta()
        self.assertTrue(copia.boleta_provisao.all().exists())
        self.assertTrue(copia.boleta_CPR.all().exists())
        self.assertTrue(copia.relacao_quantidade.all().exists())
        self.assertTrue(copia.relacao_movimentacao.all().exists())

class BoletaRendaFixaLocalUnitTest(TestCase):
    """
    Classe de Unit Test de BoletaRendaFixaLocal
    """
    def setUp(self):
        self.boleta = mommy.make('boletagem.BoletaRendaFixaLocal',
            data_operacao=datetime.date(year=2018, month=10, day=8),
            data_liquidacao=datetime.date(year=2018, month=10, day=8),
            operacao='C',
            quantidade=1000,
            preco=decimal.Decimal(9733.787491),
            taxa=decimal.Decimal(6.4)
        )

    def test_clean_data_liquidacao(self):
        copia = self.boleta
        copia.id = None
        copia.data_liquidacao = copia.data_operacao - datetime.timedelta(days=1)
        copia.save()
        self.assertRaises(ValidationError, copia.clean_data_liquidacao)

    def test_alinha_operacao_quantidade(self):
        """
        Testa a validação do campo quantidade.
        """
        boleta_copia = self.boleta
        boleta_copia.id = None
        boleta_copia.operacao = 'V'
        boleta_copia.quantidade = 1000
        boleta_copia.clean_quantidade()
        self.assertEqual(-1000, boleta_copia.quantidade)
        self.assertEqual('V', boleta_copia.operacao)
        boleta_copia.operacao = 'C'
        boleta_copia.quantidade = -1000
        boleta_copia.clean_quantidade()
        self.assertEqual(1000, boleta_copia.quantidade)
        self.assertEqual('C', boleta_copia.operacao)

    def test_clean_preco(self):
        copia = self.boleta
        copia.id = None
        copia.preco = -10
        self.assertRaises(ValidationError, copia.clean_preco)
        copia.preco = 12.1234567890
        copia.clean_preco()
        self.assertEqual(copia.preco, decimal.Decimal('12.1234567890').quantize(decimal.Decimal('1.000000')))

    def test_cria_movimentacao(self):
        """
        Testa se o método cria_movimentacao cria uma movimentação do ativo.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.criar_movimentacao()
        self.assertTrue(copia.relacao_movimentacao.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        mov = fm.Movimentacao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(mov, fm.Movimentacao)
        self.assertEqual(mov.valor, round(copia.quantidade * copia.preco + copia.corretagem, 2))
        self.assertEqual(mov.fundo, copia.fundo)
        self.assertEqual(mov.data, copia.data_operacao)
        self.assertEqual(mov.content_object, copia)
        self.assertEqual(mov.objeto_movimentacao, copia.ativo)

    def test_cria_quantidade(self):
        """
        Testa se o método cria_quantidade cria uma quantidade do ativo.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_quantidade.all().exists())
        copia.criar_quantidade()
        self.assertTrue(copia.relacao_quantidade.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        qtd = fm.Quantidade.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(qtd, fm.Quantidade)
        self.assertEqual(qtd.qtd, copia.quantidade)
        self.assertEqual(qtd.fundo, copia.fundo)
        self.assertEqual(qtd.data, copia.data_operacao)
        self.assertEqual(qtd.content_object, copia)
        self.assertEqual(qtd.objeto_quantidade, copia.ativo)

    def test_criar_boleta_CPR(self):
        """
        Testa se a boleta de renda fixa local gera a boleta de CPR corerspondente
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.fundo, copia.fundo)
        self.assertEqual(cpr.data_inicio, copia.data_operacao)
        self.assertEqual(cpr.data_pagamento, copia.data_liquidacao)
        self.assertEqual(cpr.content_object, copia)

    def test_criar_provisao(self):
        """
        Testa se a boleta de provisão é criada corretamente.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        copia.criar_boleta_provisao()
        self.assertTrue(copia.boleta_provisao.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        provisao = bm.BoletaProvisao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(provisao, bm.BoletaProvisao)
        self.assertEqual(provisao.financeiro, round(-(copia.preco*copia.quantidade) + copia.corretagem,2))

    def test_fechar_boleta(self):
        """
        Testa se a função de fechamento de boleta gera as quantidades, movimentações
        e boletas.
        """
        copia = self.boleta
        copia.id = None
        copia.preco = '9733.787491'
        copia.taxa = '6.4'
        copia.full_clean()
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        self.assertFalse(copia.boleta_CPR.all().exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())

class BoletaRendaFixaOffshoreUnitTest(TestCase):
    """
    Classe de Unit Test de BoletaRendaFixaOffshore
    """
    def setUp(self):
        self.boleta = mommy.make('boletagem.BoletaRendaFixaOffshore',
            data_operacao=datetime.date(year=2018, month=10, day=8),
            data_liquidacao=datetime.date(year=2018, month=10, day=9),
            operacao='C',
            quantidade=1000,
            preco=decimal.Decimal(0.994594),
            taxa=2.133
        )

    def test_clean_data_liquidacao(self):
        """
        Testa o método de validação da data de liquidação da boleta.
        """
        copia = self.boleta
        copia.id = None
        copia.data_liquidacao = copia.data_operacao - datetime.timedelta(days=1)
        self.assertRaises(ValidationError, self.boleta.clean_data_liquidacao)

    def test_clean_operacao_quantidade(self):
        """
        Testa se o método de validação de quantidade alinha corretamente
        o valor da quantidade com a operação. Em operações de compra, a
        quantidade deve ser um valor positivo, e, em operações de venda,
        o valor deve ser negativo.
        """
        copia = self.boleta
        copia.id = None
        self.assertEqual(copia.operacao, "C")
        self.assertGreater(copia.quantidade, 0)
        # Boleta a quantidade como negativa.
        copia.quantidade = -copia.quantidade
        # Método clean deve corrigir a quantidade para alinhar com a operação.
        copia.clean_quantidade()
        self.assertEqual(copia.operacao, "C")
        self.assertGreater(copia.quantidade, 0)

        copia.operacao = "V"
        # Método clean deve corrigir a quanidade para alinhar com a operação
        copia.clean_quantidade()
        self.assertEqual(copia.operacao, "V")
        self.assertLess(copia.quantidade, 0)

    def test_clean_preco(self):
        """
        Testa a validação do preço da boleta
        """
        copia = self.boleta
        copia.id = None
        copia.preco = -abs(copia.preco)
        self.assertRaises(ValidationError, copia.clean_preco)
        copia.preco = 12.1234567890
        copia.clean_preco()
        self.assertEqual(copia.preco, decimal.Decimal('12.1234567890').quantize(decimal.Decimal('1.000000')))

    def test_cria_movimentacao(self):
        """
        Testa se o método cria_movimentacao cria uma movimentação do ativo.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.criar_movimentacao()
        self.assertTrue(copia.relacao_movimentacao.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        mov = fm.Movimentacao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(mov, fm.Movimentacao)
        self.assertEqual(mov.valor, round(copia.quantidade * copia.preco + copia.corretagem, 2))
        self.assertEqual(mov.fundo, copia.fundo)
        self.assertEqual(mov.data, copia.data_operacao)
        self.assertEqual(mov.content_object, copia)
        self.assertEqual(mov.objeto_movimentacao, copia.ativo)

    def test_cria_quantidade(self):
        """
        Testa se o método cria_quantidade cria uma quantidade do ativo.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_quantidade.all().exists())
        copia.criar_quantidade()
        self.assertTrue(copia.relacao_quantidade.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        qtd = fm.Quantidade.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(qtd, fm.Quantidade)
        self.assertEqual(qtd.qtd, copia.quantidade)
        self.assertEqual(qtd.fundo, copia.fundo)
        self.assertEqual(qtd.data, copia.data_operacao)
        self.assertEqual(qtd.content_object, copia)
        self.assertEqual(qtd.objeto_quantidade, copia.ativo)

    def test_criar_boleta_CPR(self):
        """
        Testa se a boleta de renda fixa local gera a boleta de CPR corerspondente
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.fundo, copia.fundo)
        self.assertEqual(cpr.data_inicio, copia.data_operacao)
        self.assertEqual(cpr.data_pagamento, copia.data_liquidacao)
        self.assertEqual(cpr.content_object, copia)

    def test_criar_provisao(self):
        """
        Testa se a boleta de provisão é criada corretamente.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        copia.criar_boleta_provisao()
        self.assertTrue(copia.boleta_provisao.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        provisao = bm.BoletaProvisao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(provisao, bm.BoletaProvisao)
        self.assertEqual(provisao.financeiro, round(-(copia.preco*copia.quantidade) + copia.corretagem,2))

    def test_fechar_boleta(self):
        copia = self.boleta
        copia.id = None
        copia.clean_preco()
        copia.clean_taxa()
        copia.full_clean()
        copia.save()
        self.assertFalse(copia.fechado())
        copia.fechar_boleta()
        self.assertTrue(copia.fechado())

class BoletaFundoLocalUnitTest(TestCase):
    """
    Classe de Unit Test de BoletaFundoLocal. Assume que as boletas foram
    full_cleaned e salvas no sistema.
    O fechamento da boleta de fundo local, pode haver 4 cenários possíveis:
    1 - Ativo negociado é fundo gerido:
        - Cota da movimentação ainda não está disponível. O fechamento não
        poder ser completo. Gera apenas a boleta de provisão e CPR.
        - Cota da movimentação foi disponibilizada. Deve criar a movimentação
        e a quantidade do ativo gerido para o fundo executando a movimentação.
        Deve criar também a boleta de passivo do fundo operado.
    2 - Ativo negociado não é fundo gerido:
        - Similar ao primeiro caso, mas não é gerado boleta de passivo em
        momento algum.

    TODO: Necessário testar também quando há resgate, aplicação e resgate total.

    """
    def setUp(self):
        # Setup de fundos geridos e não geridos
        self.gestora_anima = mommy.make('fundo.Gestora',
            nome='SPN',
            anima=True
        )
        self.gestora_qualquer = mommy.make('fundo.Gestora',
            anima=False
        )
        self.fundo_gerido = mommy.make('fundo.Fundo',
            nome='Veredas',
            gestora=self.gestora_anima,
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            categoria="Fundo de Ações"
        )
        self.fundo_qualquer = mommy.make('fundo.Fundo',
            gestora=self.gestora_qualquer
        )
        self.ativo_fundo_gerido = mommy.make('ativos.Fundo_Local',
            gestao=self.fundo_gerido
        )
        self.ativo_fundo_qualquer = mommy.make('ativos.Fundo_Local',
            gestao=self.fundo_qualquer
        )

        # Setup de boleta completa.
        self.boleta = mommy.make('boletagem.BoletaFundoLocal',
            ativo=self.ativo_fundo_qualquer,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao="Aplicação",
            quantidade=1000,
            preco=1300,
            financeiro=-1000*1300
        )
        self.boleta.full_clean()
        self.boleta.save()
        # Setup
        self.boleta_sem_cota_com_preco = mommy.make('boletagem.BoletaFundoLocal',
            ativo=self.ativo_fundo_qualquer,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao="Aplicação",
            financeiro=1300000
        )
        self.boleta_sem_cota_com_preco.full_clean()
        self.boleta_sem_cota_com_preco.save()
        preco = mommy.make('mercado.Preco',
            ativo=self.boleta_sem_cota_com_preco.ativo,
            preco_fechamento=1300,
            data_referencia=self.boleta_sem_cota_com_preco.data_cotizacao
        )
        preco.save()

        self.boleta_sem_cota_sem_preco = mommy.make('boletagem.BoletaFundoLocal',
            ativo=self.ativo_fundo_qualquer,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=17),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao="Aplicação",
            financeiro=1300000
        )
        self.boleta_sem_cota_sem_preco.full_clean()
        self.boleta_sem_cota_sem_preco.save()

        self.boleta_ativo_gerido = mommy.make('boletagem.BoletaFundoLocal',
            ativo=self.ativo_fundo_gerido,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao="Aplicação",
            quantidade=1000,
            preco=1300
        )
        self.boleta_ativo_gerido.full_clean()
        self.boleta_ativo_gerido.save()
        # Setup
        self.boleta_sem_cota_gerido = mommy.make('boletagem.BoletaFundoLocal',
            ativo=self.ativo_fundo_gerido,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=17),
            data_liquidacao=datetime.date(year=2018, month=10, day=20),
            operacao="Aplicação",
            financeiro=1300000
        )
        self.boleta_sem_cota_gerido.full_clean()
        self.boleta_sem_cota_gerido.save()

        self.boleta_sem_cota_gerido_com_preco = mommy.make('boletagem.BoletaFundoLocal',
            ativo=self.ativo_fundo_gerido,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao="Aplicação",
            financeiro=1300000
        )
        self.boleta_sem_cota_gerido_com_preco.full_clean()
        self.boleta_sem_cota_gerido_com_preco.save()
        preco = mommy.make('mercado.Preco',
            ativo=self.boleta_sem_cota_gerido_com_preco.ativo,
            preco_fechamento=1300,
            data_referencia=self.boleta_sem_cota_com_preco.data_cotizacao
        )
        preco.save()

    def test_clean_financeiro_sem_quantidade_validation_exception(self):
        """
        Testa o método de validação do campo financeiro. Testa se a validação
        levanta uma exceção quando o financeiro está em branco, assim como a
        quantidade.
        """
        # Preenche boleta com
        copia = self.boleta
        copia.id = None
        copia.quantidade = None
        copia.financeiro = None
        self.assertRaises(ValidationError, copia.clean_financeiro)

    def test_clean_financeiro_calcula_financeiro(self):
        """
        Testa o método de validação do campo financeiro. Caso a quantidade
        e preço estejam preenchidos, o financeiro é calculado.
        """
        copia = self.boleta
        copia.id = None
        copia.financeiro = None
        copia.preco = 1200
        copia.clean_financeiro()
        self.assertEqual(copia.financeiro, copia.preco * copia.quantidade)

    def test_clean_data_liquidacao_validation_error(self):
        """
        Testa a validação da data de liquidação. Ela deve ser menor ou igual
        à data de operação
        """
        copia = self.boleta
        copia.id = None
        copia.data_liquidacao = copia.data_operacao - datetime.timedelta(days=1)
        self.assertRaises(ValidationError, copia.clean_data_liquidacao)

    def test_clean_data_cotizacao_validation_error_data_operacao(self):
        """
        Testa a validação da data de cotização. Ela deve ser menor ou igual
        à data de operação
        """
        copia = self.boleta
        copia.id = None
        copia.data_cotizacao = copia.data_operacao - datetime.timedelta(days=1)
        self.assertRaises(ValidationError, copia.clean_data_cotizacao)

    def test_clean_data_cotizacao_validation_error_resgate(self):
        """
        Testa a validação da data de cotização. Se a operação for de resgate,
        a data de cotização deve ser menor ou igual que a data de liquidação.
        """
        copia = self.boleta
        copia.id = None
        copia.operacao = "Resgate"
        copia.data_liquidacao = copia.data_cotizacao - datetime.timedelta(days=1)
        self.assertRaises(ValidationError, copia.clean_data_cotizacao)
        copia.operacao = "Resgate total"
        self.assertRaises(ValidationError, copia.clean_data_cotizacao)

    def test_alinhamento_operacao_quantidade(self):
        """
        Testa se a a função clean corrige o alinhamento de operação
        e quantidade.
        """
        copia = self.boleta
        copia.id = None
        copia.operacao = "Resgate"
        copia.quantidade = 1000
        copia.clean_quantidade()
        self.assertEqual(-1000, copia.quantidade)
        self.assertEqual("Resgate", copia.operacao)
        copia.operacao = "Aplicação"
        copia.quantidade = -1000
        copia.clean_quantidade()
        self.assertEqual(1000, copia.quantidade)
        self.assertEqual("Aplicação", copia.operacao)

    def test_cria_movimentacao(self):
        """
        Testa se a boleta gera movimentação corretamente.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.criar_movimentacao()
        self.assertTrue(copia.relacao_movimentacao.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        mov = fm.Movimentacao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(mov, fm.Movimentacao)
        self.assertEqual(mov.valor, round(copia.financeiro, 2))
        self.assertEqual(mov.fundo, copia.fundo)
        self.assertEqual(mov.data, copia.data_cotizacao)
        self.assertEqual(mov.content_object, copia)
        self.assertEqual(mov.objeto_movimentacao, copia.ativo)

    def test_cria_quantidade(self):
        """
        Testa se a boleta cria quantidades corretamente.

        """
        # TODO:Tem que ver se há valor de cota do fundo disponível para
        # calcular a quantidade correta.
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_quantidade.all().exists())
        copia.criar_quantidade()
        self.assertTrue(copia.relacao_quantidade.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        qtd = fm.Quantidade.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(qtd, fm.Quantidade)
        self.assertEqual(qtd.qtd, copia.quantidade)
        self.assertEqual(qtd.fundo, copia.fundo)
        self.assertEqual(qtd.data, copia.data_cotizacao)
        self.assertEqual(qtd.content_object, copia)
        self.assertEqual(qtd.objeto_quantidade, copia.ativo)

    def test_cria_boleta_CPR_cotizacao_antes_liquidacao(self):
        """
        Testa se conseguimos criar uma boleta de CPR com as características
        corretas da boleta de operação de fundo. Neste caso, a boleta do fundo
        possui data de cotização anterior à data de liquidação.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.valor_cheio, copia.financeiro)
        self.assertEqual(cpr.fundo, copia.fundo)
        self.assertEqual(cpr.data_inicio, copia.data_cotizacao)
        self.assertEqual(cpr.data_pagamento, copia.data_liquidacao)
        self.assertEqual(cpr.content_object, copia)

    def test_cria_boleta_CPR_liquidacao_antes_cotizacao(self):
        """
        Testa se conseguimos criar uma boleta de CPR com as características
        corretas da boleta de operação de fundo. Neste caso, a boleta do fundo
        possui data de liquidação anterior à data de cotização. A operação
        deve ser de aplicação apenas.
        """
        copia = self.boleta
        copia.id = None
        copia.data_liquidacao = copia.data_cotizacao - datetime.timedelta(days=1)
        copia.operacao = "Aplicação"
        copia.save()
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.valor_cheio, copia.financeiro)
        self.assertEqual(cpr.fundo, copia.fundo)
        self.assertEqual(cpr.data_inicio, copia.data_liquidacao)
        self.assertEqual(cpr.data_pagamento, copia.data_cotizacao)
        self.assertEqual(cpr.content_object, copia)

    def test_cria_boleta_provisao(self):
        """
        Testa se a boleta de provisão criada é criada com os parametros corretos.
        """
        # Verifica se não há boleta associada.
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        copia.criar_boleta_provisao()
        self.assertTrue(copia.boleta_provisao.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        provisao = bm.BoletaProvisao.objects.get(content_type__pk=tipo.id, object_id=copia.id)
        self.assertEqual(-provisao.financeiro, copia.financeiro)
        self.assertEqual(provisao.caixa_alvo, copia.caixa_alvo)
        self.assertEqual(provisao.data_pagamento, copia.data_liquidacao)
        self.assertEqual(provisao.fundo, copia.fundo)

    def test_fechar_boleta_com_cota_ativo_gerido(self):
        """
        Testa se o fechamento normal de boleta de fundo local gerido cria as
        movimentações, quantidades e boletas corretamente.
        """
        copia = self.boleta_ativo_gerido
        copia.id = None
        copia.save()
        self.assertFalse(copia.fechado())
        copia.fechar_boleta()
        self.assertTrue(copia.fechado())

    def test_fechar_boleta_sem_cota_ativo_gerido_sem_preco_no_sistema(self):
        """
        No caso de fechamento de boleta sem cota, as boletas geradas são
        apenas de CPR e provisão, sem geração de quantidade, movimentação
        ou boleta de passivo.
        """
        copia = self.boleta_sem_cota_gerido
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        self.assertFalse(copia.boleta_CPR.all().exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        self.assertFalse(copia.relacao_passivo.all().exists())
        copia.fechar_boleta()
        self.assertTrue(copia.boleta_provisao.all().exists())
        self.assertTrue(copia.boleta_CPR.all().exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        self.assertFalse(copia.relacao_passivo.all().exists())
        self.assertFalse(copia.fechado())

    def test_fechar_boleta_sem_cota_ativo_gerido_com_preco_no_sistema(self):
        """
        Testa fechamento de boleta quando o preço está disponível, mas a
        boleta está incompleta. Deve conseguir pegar o preço e atualizar
        todas as informações, e ser capaz de gerar todos os objetos
        corretamente.
        """
        copia = self.boleta_sem_cota_gerido_com_preco
        copia.id = None
        copia.save()
        self.assertFalse(copia.fechado())
        copia.fechar_boleta()
        self.assertTrue(copia.fechado())

    def test_fechar_boleta_com_cota_ativo_nao_gerido(self):
        """
        Testa se, ao fechar uma boleta simples, de movimentação em fundo não
        gerido, o fechamento cria as movimentações, quantidades e boletas
        necessárias.
        """
        copia = self.boleta
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.fechado())
        copia.fechar_boleta()
        self.assertTrue(copia.fechado())

    def test_fechar_boleta_sem_cota_ativo_nao_gerido_sem_preco(self):
        """
        Testa se, ao fechar uma boleta sem informação de cota, ela ainda não é
        considerada fechada. Ela só deve ser considerada fechada se tiver
        cotizado corretamente.
        """
        copia = self.boleta_sem_cota_sem_preco
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_provisao.all().exists())
        self.assertFalse(copia.boleta_CPR.all().exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        self.assertFalse(copia.relacao_passivo.all().exists())
        copia.fechar_boleta()
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        self.assertFalse(copia.relacao_passivo.all().exists())
        self.assertTrue(copia.boleta_provisao.all().exists())
        self.assertTrue(copia.boleta_CPR.all().exists())

    def test_fechar_boleta_sem_cota_ativo_nao_gerido_com_preco(self):
        """
        Boletas incompletas mas com o preço no sistema devem criar todos
        os objetos relacionados, e deve fechar corretamente.
        """
        copia = self.boleta_sem_cota_com_preco
        copia.id = None
        copia.save()
        self.assertFalse(copia.fechado())
        copia.fechar_boleta()
        self.assertTrue(copia.fechado())

    def test_cria_boleta_passivo(self):
        """
        Testa se, ao fechar a boleta com todas as informações necessárias,
        uma boleta de passivo é gerada.
        """
        copia = self.boleta_ativo_gerido
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_passivo.all().exists())
        copia.criar_boleta_passivo()
        self.assertTrue(copia.relacao_passivo.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        passivo = bm.BoletaPassivo.objects.get(content_type__pk=tipo.id, object_id=copia.id)
        # O nome do fundo é o nome do cotista.
        self.assertEqual(passivo.cotista.nome, copia.fundo.nome)
        self.assertEqual(passivo.valor, copia.financeiro)
        self.assertEqual(passivo.data_movimentacao, copia.data_operacao)
        self.assertEqual(passivo.data_cotizacao, copia.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, copia.data_liquidacao)
        self.assertEqual(passivo.operacao, copia.operacao)
        self.assertEqual(passivo.fundo.id, copia.ativo.gestao.id)
        self.assertEqual(passivo.cota, copia.preco)
        self.assertEqual(passivo.content_object, copia)

    @pytest.mark.xfail
    def test_resgate_total(self):
        """
        Testa se o resgate total calcula a quantidade financeira correta.
        """
        self.assertTrue(False)

class BoletaFundoOffshoreUnitTest(TestCase):
    """
    Classe de Unit Tests da BoletaFundoOffshore
    """
    def setUp(self):
        qtd = decimal.Decimal('1000').quantize(decimal.Decimal('1.000000'))
        price = decimal.Decimal('1300').quantize(decimal.Decimal('1.000000'))
        self.boleta = mommy.make('boletagem.BoletaFundoOffshore',
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            quantidade=qtd,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0],
            preco=price,
            financeiro=decimal.Decimal(qtd*price).quantize(decimal.Decimal('1.000000'))
        )

        # Setup de fundos geridos e não geridos
        self.gestora_anima = mommy.make('fundo.Gestora',
            nome='SPN',
            anima=True
        )

        self.fundo_gerido = mommy.make('fundo.Fundo',
            nome='Veredas',
            gestora=self.gestora_anima,
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            categoria="Fundo de Ações"
        )

        self.ativo_fundo_gerido = mommy.make('ativos.Fundo_Offshore',
            gestao=self.fundo_gerido
        )

        self.boleta_ativo_gerido = mommy.make('boletagem.BoletaFundoOffshore',
            ativo=self.ativo_fundo_gerido,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            quantidade=qtd,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0],
            preco=price,
            financeiro=decimal.Decimal(qtd*price).quantize(decimal.Decimal('1.000000'))
        )

        gestora_qualquer = mommy.make('fundo.Gestora',
            anima=False
        )

        fundo_qualquer = mommy.make('fundo.Fundo',
            gestora=gestora_qualquer
        )

        ativo_fundo_qualquer = mommy.make('ativos.Fundo_Offshore',
            gestao=fundo_qualquer
        )
        self.boleta_ativo_qualquer = mommy.make('boletagem.BoletaFundoOffshore',
            ativo=ativo_fundo_qualquer,
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=19),
            operacao=bm.BoletaFundoOffshore.OPERACAO[0][0],
            quantidade=qtd,
            estado=bm.BoletaFundoOffshore.ESTADO[4][0],
            preco=price,
            financeiro=decimal.Decimal(qtd*price).quantize(decimal.Decimal('1.000000'))
        )

    def test_alinha_operacao_quantidade(self):
        """
        Testa se o método de validação da quantidade corrige o valor da
        quantidade de acordo com a operação.
        """
        copia = self.boleta
        copia.id = None
        copia.operacao = "Aplicação"
        copia.quantidade = -1000
        copia.clean_quantidade()
        self.assertEqual(copia.quantidade, 1000)
        self.assertEqual(copia.operacao, "Aplicação")
        copia.operacao = "Resgate"
        copia.quantidade = 1000
        copia.clean_quantidade()
        self.assertEqual(copia.quantidade, -1000)
        self.assertEqual(copia.operacao, "Resgate")

    def test_atualizar_preco_quantidade(self):
        """
        Quando o preço da cota for disponibilizado, testa se o método atualizar()
        atualiza o preço e quantidade de cotas na boleta.
        """
        copia = self.boleta
        copia.id = None
        copia.quantidade = None
        preco = mommy.make('mercado.Preco',
            ativo=copia.ativo,
            data_referencia=copia.data_cotizacao,
            preco_fechamento=copia.preco
        )
        preco.full_clean()
        preco.save()
        copia.preco = None
        copia.save()
        self.assertEqual(copia.preco, None)
        self.assertEqual(copia.quantidade, None)
        copia.atualizar()
        self.assertEqual(copia.preco, preco.preco_fechamento)
        self.assertEqual(copia.quantidade, (copia.financeiro/preco.preco_fechamento).quantize(decimal.Decimal('1.000000')))

    def test_cria_quantidade(self):
        """
        Testa o método de criação de quantidade da boleta. Para fundo offshore,
        o preço de cotização deve estar disponível para que a quantidade seja
        criada. Assume que há preço disponível. Assume que a boleta em questão
        foi salva antes de criar a quantidade.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_quantidade.all().exists())
        copia.criar_quantidade()
        self.assertTrue(copia.relacao_quantidade.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        qtd = fm.Quantidade.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(qtd, fm.Quantidade)
        self.assertEqual(qtd.qtd, copia.quantidade)
        self.assertEqual(qtd.fundo, copia.fundo)
        self.assertEqual(qtd.data, copia.data_cotizacao)
        self.assertEqual(qtd.content_object, copia)
        self.assertEqual(qtd.objeto_quantidade, copia.ativo)

    def test_cria_movimentacao(self):
        """
        Testa o método de criação de movimentação da boleta.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.criar_movimentacao()
        self.assertTrue(copia.relacao_movimentacao.all().exists())
        tipo = ContentType.objects.get_for_model(copia)
        mov = fm.Movimentacao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(mov, fm.Movimentacao)
        self.assertEqual(mov.valor, copia.financeiro)
        self.assertEqual(mov.fundo, copia.fundo)
        self.assertEqual(mov.data, copia.data_cotizacao)

    def test_cria_boleta_CPR_cotizacao(self):
        """
        Testa o método para criação de boleta de CPR para cotização da
        movimentação. A boleta criada não tem data de pagamento.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR_cotizacao()
        self.assertTrue(copia.boleta_CPR.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.valor_cheio, copia.financeiro)
        self.assertEqual(cpr.data_inicio, copia.data_cotizacao)
        self.assertEqual(cpr.fundo, copia.fundo)

    def test_cria_boleta_CPR_liquidacao(self):
        """
        Testa o método para criação de boleta de CPR para liquidação
        da movimentação.
        """
        copia = self.boleta
        copia.id = None
        copia.save()
        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR_liquidacao()
        self.assertTrue(copia.boleta_CPR.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.valor_cheio, -copia.financeiro.quantize(decimal.Decimal('1.00')))
        self.assertEqual(cpr.data_inicio, copia.data_cotizacao)
        self.assertEqual(cpr.data_pagamento, copia.data_liquidacao)
        self.assertEqual(cpr.fundo, copia.fundo)

    def test_passivo(self):
        """
        Testa o método passivo
        """
        self.assertTrue(self.boleta_ativo_gerido.passivo())
        self.assertFalse(self.boleta_ativo_qualquer.passivo())

    def test_cria_boleta_passivo(self):
        """
        Testa se consegue criar uma boleta de passivo com as informações
        corretas
        """
        # Cria boleta de movimentação de fundo offshore com ativo gerido
        copia = self.boleta_ativo_gerido
        copia.id = None
        copia.save()
        # Verifica que não havia boleta de passivo antes.
        self.assertFalse(copia.boleta_passivo.all().exists())
        copia.criar_boleta_passivo()
        # Verifica que foi criado boleta de passivo.
        self.assertTrue(copia.boleta_passivo.all().exists())

        # Buscando a boleta.
        tipo = ContentType.objects.get_for_model(copia)
        passivo = bm.BoletaPassivo.objects.get(content_type__pk=tipo.id,
            object_id=copia.id)

        self.assertEqual(passivo.cotista.nome, copia.fundo.nome)
        self.assertEqual(passivo.valor, copia.financeiro)
        self.assertEqual(passivo.data_movimentacao, copia.data_operacao)
        self.assertEqual(passivo.data_cotizacao, copia.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, copia.data_liquidacao)
        self.assertEqual(passivo.operacao, copia.operacao)
        self.assertEqual(passivo.fundo.id, copia.ativo.gestao.id)
        self.assertEqual(passivo.cota, copia.preco)
        self.assertEqual(passivo.content_object, copia)

    def test_fechamento_transicao_1(self):
        """
        Testa o fechamento da transição de estado 'Pendente de cotização e
        liquidação' -> 'pendente de cotização'
        (Data de liquidação anterior à data de cotização)
        Condições necessárias:
            - Valor financeiro a liquidar.
            - Fechamento na data de liquidação.
        Tarefas a executar:
            - Cria a boleta de provisão, para a saída de caixa.
            - Cria a boleta de CPR de cotização com data de início igual
            à data de liquidação, e sem data de pagamento, que deve ser
            atualizada quando o preço da cota for disponibilizado.
            - Atualizar estado.
        """
        copia = self.boleta
        copia.id = None
        copia.data_liquidacao = datetime.date(year=2018, month=10, day=16)
        copia.data_cotizacao = datetime.date(year=2018, month=10, day=19)
        data_fechamento = copia.data_liquidacao
        copia.preco = None
        copia.quantidade = None
        copia.save()

        self.assertFalse(copia.boleta_provisao.all().exists())
        self.assertFalse(copia.boleta_CPR.all().exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        self.assertEqual(copia.estado, bm.BoletaFundoOffshore.ESTADO[4][0])
        copia.fechar_boleta(data_referencia=data_fechamento)
        self.assertTrue(copia.boleta_provisao.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        prov = bm.BoletaProvisao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(prov, bm.BoletaProvisao)
        self.assertEqual(prov.financeiro, -copia.financeiro.quantize(decimal.Decimal('1.00')))
        self.assertEqual(prov.fundo, copia.fundo)
        self.assertEqual(prov.data_pagamento, copia.data_liquidacao)
        self.assertEqual(prov.caixa_alvo, copia.caixa_alvo)

        self.assertTrue(copia.boleta_CPR.all().filter(valor_cheio=copia.financeiro).exists())

        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id,
            object_id=copia.id, valor_cheio=copia.financeiro)

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.valor_cheio, copia.financeiro.quantize(decimal.Decimal('1.00')))
        self.assertEqual(cpr.fundo, copia.fundo)
        self.assertEqual(cpr.data_inicio, copia.data_liquidacao)
        self.assertIn("Cotização", cpr.descricao)
        self.assertIn(copia.ativo.nome, cpr.descricao)

        self.assertEqual(copia.estado, bm.BoletaFundoOffshore.ESTADO[0][0])

    def test_fechamento_transicao_2(self):
        """
        Testa o fechamento nas condições da transição 2.
        Transição 2 - Pendente de cotização e liquidação -> pendente de liquidação.
            (Data de cotização anterior à data de liquidação)
            Condições necessárias:
                - Valor financeiro a liquidar disponível
                - Valor das cotas disponível.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Cria a boleta de provisão, para saída de caixa.
                - Cria a boleta de CPR de liquidação, com valor financeiro inverso
                à boleta de operação.
                - Cria a quantidade e movimentação do ativo.
                - Atualizar estado.
        """
        copia = self.boleta_ativo_qualquer
        copia.id = None
        data_fechamento = copia.data_cotizacao
        copia.estado = copia.ESTADO[4][0]
        copia.save()

        self.assertFalse(copia.boleta_provisao.all().exists())
        self.assertFalse(copia.boleta_CPR.all().filter(valor_cheio=-copia.financeiro).exists())
        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        self.assertEqual(copia.estado, bm.BoletaFundoOffshore.ESTADO[4][0])

        copia.fechar_boleta(data_referencia=data_fechamento)

        self.assertTrue(copia.boleta_provisao.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        prov = bm.BoletaProvisao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertIsInstance(prov, bm.BoletaProvisao)
        self.assertEqual(prov.financeiro, -copia.financeiro)
        self.assertEqual(prov.fundo, copia.fundo)
        self.assertEqual(prov.data_pagamento, copia.data_liquidacao)
        self.assertEqual(prov.caixa_alvo, copia.caixa_alvo)

        self.assertTrue(copia.boleta_CPR.all().filter(valor_cheio=-copia.financeiro).exists())

        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, \
            object_id=copia.id, valor_cheio=-copia.financeiro.quantize(decimal.Decimal('1.00')))

        self.assertIsInstance(cpr, bm.BoletaCPR)
        self.assertEqual(cpr.valor_cheio, -copia.financeiro.quantize(decimal.Decimal('1.00')))
        self.assertEqual(cpr.fundo, copia.fundo)
        self.assertEqual(cpr.data_inicio, copia.data_cotizacao)
        self.assertEqual(cpr.data_pagamento, copia.data_liquidacao)
        self.assertIn("Liquidação", cpr.descricao)
        self.assertIn(copia.ativo.nome, cpr.descricao)

        self.assertTrue(copia.relacao_quantidade.all().exists())

        qtd = fm.Quantidade.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertTrue(qtd.qtd, copia.quantidade)
        self.assertTrue(qtd.fundo, copia.fundo)
        self.assertTrue(qtd.data, copia.data_cotizacao)
        self.assertTrue(qtd.objeto_quantidade, copia.ativo)
        self.assertTrue(qtd.content_object, copia)

        self.assertTrue(copia.relacao_movimentacao.all().exists())

        mov = fm.Movimentacao.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertTrue(mov.valor, copia.financeiro)
        self.assertTrue(mov.fundo, copia.fundo)
        self.assertTrue(mov.data, copia.data_cotizacao)
        self.assertTrue(mov.content_object, copia)
        self.assertTrue(mov.objeto_movimentacao, copia.ativo)

        self.assertEqual(copia.estado, bm.BoletaFundoOffshore.ESTADO[1][0])

    def test_fechamento_transicao_2_ativo_gerido(self):
        """
        Testa o fechamento nas condições da transição 2.
        Transição 2 - Pendente de cotização e liquidação -> pendente de liquidação.
            (Data de cotização anterior à data de liquidação)
            Condições necessárias:
                - Valor financeiro a liquidar disponível
                - Valor das cotas disponível.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Cria a boleta de provisão, para saída de caixa.
                - Cria a boleta de CPR de liquidação, com valor financeiro inverso
                à boleta de operação.
                - Cria a quantidade e movimentação do ativo.
                - Atualizar estado.
        """
        copia = self.boleta_ativo_gerido
        copia.id = None
        data_fechamento = copia.data_cotizacao
        copia.estado = copia.ESTADO[4][0]
        copia.save()

        self.assertFalse(copia.boleta_passivo.all().exists())

        copia.fechar_boleta(data_referencia=data_fechamento)

        self.assertTrue(copia.boleta_passivo.all().exists())

        tipo = ContentType.objects.get_for_model(copia)

        passivo = bm.BoletaPassivo.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertEqual(passivo.valor, copia.financeiro)
        self.assertEqual(passivo.operacao, copia.operacao)
        self.assertEqual(passivo.data_movimentacao, copia.data_operacao)
        self.assertEqual(passivo.data_cotizacao, copia.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, copia.data_liquidacao)
        self.assertEqual(passivo.fundo, copia.ativo.gestao)
        self.assertEqual(passivo.cota, copia.preco)
        self.assertEqual(passivo.content_object, copia)

    def test_fechamento_transicao_3(self):
        """
        Transição 3 - Pendente de cotização -> Concluído
            Condições necessárias:
                - Valor de cota disponível na data de cotização.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Atualiza a boleta de CPR de cotização com a data de pagamento igual
            à data de cotização.
                - Cria a movimentação e a quantidade do ativo.
                - Atualizar estado.
        """
        # Criando a boleta no estado Pendente de cotização
        copia = self.boleta_estado_pendente_de_cotizacao()
        preco = decimal.Decimal('1300').quantize(decimal.Decimal('1.000000'))
        # Cria preço para refletir as pré-condições.
        preco = mommy.make('mercado.Preco',
            ativo=copia.ativo,
            data_referencia=copia.data_cotizacao,
            preco_fechamento=preco
        )
        preco.full_clean()
        preco.save()

        # Deve colocar a boleta no estado Pendente de cotização
        copia.fechar_boleta(copia.data_liquidacao)
        self.assertEqual(copia.ESTADO[0][0], bm.BoletaFundoOffshore.ESTADO[0][0])

        self.assertFalse(copia.relacao_quantidade.all().exists())
        self.assertFalse(copia.relacao_movimentacao.all().exists())
        copia.fechar_boleta(copia.data_cotizacao)

        tipo = ContentType.objects.get_for_model(copia)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        # Atualização da boleta de CPR com a data de pagamento
        self.assertEqual(cpr.data_pagamento, copia.data_cotizacao)
        self.assertEqual(copia.preco, preco.preco_fechamento)
        self.assertEqual(copia.quantidade, copia.financeiro/preco.preco_fechamento)

        # Verifica criação de quantidade e movimentação.
        self.assertTrue(copia.relacao_quantidade.all().exists())
        self.assertTrue(copia.relacao_movimentacao.all().exists())

    def test_fechamento_transicao_3_ativo_gerido(self):
        """
        Transição 3 - Pendente de cotização -> Concluído
            Condições necessárias:
                - Valor de cota disponível na data de cotização.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Atualiza a boleta de CPR de cotização com a data de pagamento igual
            à data de cotização.
                - Cria a movimentação e a quantidade do ativo.
                - Atualizar estado.
        """
        # Criando a boleta no estado Pendente de cotização
        copia = self.boleta_estado_pendente_de_cotizacao_ativo_gerido()
        preco = decimal.Decimal('1300').quantize(decimal.Decimal('1.000000'))
        # Cria preço para refletir as pré-condições.
        preco = mommy.make('mercado.Preco',
            ativo=copia.ativo,
            data_referencia=copia.data_cotizacao,
            preco_fechamento=preco
        )
        preco.full_clean()
        preco.save()

        # Deve colocar a boleta no estado Pendente de cotização
        copia.fechar_boleta(copia.data_liquidacao)
        self.assertEqual(copia.ESTADO[0][0], bm.BoletaFundoOffshore.ESTADO[0][0])

        self.assertFalse(copia.boleta_passivo.all().exists())
        copia.fechar_boleta(copia.data_cotizacao)
        # Verifica criação de boleta de passivo passivo.
        self.assertTrue(copia.boleta_passivo.all().exists())

        tipo = ContentType.objects.get_for_model(copia)
        passivo = bm.BoletaPassivo.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertEqual(passivo.valor, copia.financeiro)
        self.assertEqual(passivo.operacao, copia.operacao)
        self.assertEqual(passivo.data_movimentacao, copia.data_operacao)
        self.assertEqual(passivo.data_cotizacao, copia.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, copia.data_liquidacao)
        self.assertEqual(passivo.fundo, copia.ativo.gestao)
        self.assertEqual(passivo.cota, copia.preco)
        self.assertEqual(passivo.content_object, copia)

    def test_fechamento_transicao_4(self):
        """
        Transição 4 - Pendente de liquidação -> Concluído.
            Condições necessárias:
                - Liquidação da boleta de provisão.
                - Fechamento na data de liquidação.
            Tarefas a executar:
                - Atualizar estado.
        """
        # Colocando a boleta no estado pendente de liquidação.
        copia = self.boleta_estado_pendente_de_liquidacao()
        self.assertEqual(copia.estado, copia.ESTADO[1][0])

        # Liquidar a boleta na data de liquidação.
        data_fechamento = copia.data_liquidacao
        copia.fechar_boleta(data_referencia=data_fechamento)

        # Verificação da atualização.
        self.assertEqual(copia.estado, copia.ESTADO[5][0])

    def test_fechamento_transicao_5(self):
        """
        Transição 5 - Pendente de cotização -> Pendente de informação de cotização
            Condições necessárias:
                - Valor da cota indisponível no dia de cotização.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Atualizar estado.
        """
        # Colocando a boleta no estado pendente de cotização.
        copia = self.boleta_estado_pendente_de_cotizacao()
        self.assertEqual(copia.estado, copia.ESTADO[0][0])
        # Fechando a boleta na data de cotização
        data_fechamento = copia.data_cotizacao
        copia.fechar_boleta(data_fechamento)
        # Verificar se o estado foi atualizado
        print(copia.estado)
        self.assertEqual(copia.estado, copia.ESTADO[2][0])
        self.assertFalse(copia.boleta_passivo.all().exists())

    def test_fechamento_transicao_5_ativo_gerido(self):
        """
        Transição 5 - Pendente de cotização -> Pendente de informação de cotização
            Condições necessárias:
                - Valor da cota indisponível no dia de cotização.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Atualizar estado.
                - Gerar boleta de passivo.
        """
        # Colocando a boleta no estado pendente de cotização.
        copia = self.boleta_estado_pendente_de_cotizacao_ativo_gerido()
        self.assertEqual(copia.estado, copia.ESTADO[0][0])
        # Fechando a boleta na data de cotização
        data_fechamento = copia.data_cotizacao

        self.assertFalse(copia.boleta_passivo.all().exists())

        copia.fechar_boleta(data_fechamento)
        # Verificar se o estado foi atualizado
        self.assertEqual(copia.estado, copia.ESTADO[2][0])
        self.assertTrue(copia.boleta_passivo.all().exists())

        tipo = ContentType.objects.get_for_model(copia)

        passivo = bm.BoletaPassivo.objects.get(content_type__pk=tipo.id, object_id=copia.id)

        self.assertEqual(passivo.valor, copia.financeiro)
        self.assertEqual(passivo.operacao, copia.operacao)
        self.assertEqual(passivo.data_movimentacao, copia.data_operacao)
        self.assertEqual(passivo.data_cotizacao, copia.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, copia.data_liquidacao)
        self.assertEqual(passivo.fundo, copia.ativo.gestao)
        self.assertEqual(passivo.cota, copia.preco)
        self.assertEqual(passivo.content_object, copia)

    def test_fechamento_transacao_6(self):
        """
        Transição 6 - Pendente de informação de cotização -> Concluído.
            Condições necessárias:
                - Informação da cota disponibilizada.
                - Fechamento na data em que a cota é disponibilizada.
            Tarefas a executar:
                - A data de pagamento da boleta de CPR de cotização deve ser
                atualizada com a data de inserção do valor da cota.
                - A quantidade e a movimentação do ativo também são criados com base
                na data de inserção do valor da cota.
                - Atualizar estado.
        """
        boleta = self.boleta_estado_pendente_de_informacao_de_cota()
        self.assertEqual(boleta.estado, boleta.ESTADO[2][0])
        # Verifica se a função cotizavel funciona
        self.assertFalse(boleta.cotizavel())
        # Salvando o preço para disponibilizar o valor da cota no sistema.
        preco = mommy.make('mercado.Preco',
            ativo=boleta.ativo,
            data_referencia=boleta.data_cotizacao,
            preco_fechamento=decimal.Decimal('100.00').quantize(decimal.Decimal('1.000000'))
        )
        preco.full_clean()
        preco.save()
        # Verifica se a criação do preço muda o resultado da função cotizavel
        self.assertTrue(boleta.cotizavel())
        # fechando a boleta em uma data que é diferente da data de cotizacao
        self.assertFalse(preco.data_referencia==preco.criado_em)
        data_fechamento = preco.criado_em.date()
        # Verificando se a movimentação e a quantidade ainda não foram criadas.
        self.assertFalse(boleta.relacao_movimentacao.all().exists())
        self.assertFalse(boleta.relacao_quantidade.all().exists())

        boleta.fechar_boleta(data_referencia=data_fechamento)

        # Verificando o estado final da boleta.
        self.assertEqual(boleta.estado, boleta.ESTADO[5][0])

        # Pegando a boleta de CPR de cotização.
        tipo = ContentType.objects.get_for_model(boleta)
        cpr = bm.BoletaCPR.objects.get(content_type__pk=tipo.id,
            object_id=boleta.id, valor_cheio=boleta.financeiro)
        # Verificando se a data de pagamento da boleta de CPR é atualizada.
        self.assertEqual(cpr.data_pagamento, data_fechamento)
        # Verificando se a movimentacao é criada
        self.assertTrue(boleta.relacao_movimentacao.all().exists())
        # Verificando a data da movimentação criada.
        mov = fm.Movimentacao.objects.get(content_type__pk=tipo.id, object_id=boleta.id)
        self.assertEqual(mov.data, cpr.data_pagamento)
        # Verificando se a quantidade é criada
        self.assertTrue(boleta.relacao_quantidade.all().exists())
        # Verificando a data da quantidade criada.
        qtd = fm.Quantidade.objects.get(content_type__pk=tipo.id, object_id=boleta.id)
        self.assertEqual(qtd.data, cpr.data_pagamento)

    def test_fechamento_transacao_6_ativo_gerido(self):
        """
        Transição 6 - Pendente de informação de cotização -> Concluído.
            Condições necessárias:
                - Informação da cota disponibilizada.
                - Fechamento na data em que a cota é disponibilizada.
            Tarefas a executar:
                - A data de pagamento da boleta de CPR de cotização deve ser
                atualizada com a data de inserção do valor da cota.
                - A quantidade e a movimentação do ativo também são criados com base
                na data de inserção do valor da cota.
                - Atualizar estado.
                - Atualizar o valor da cota na boleta de passivo.
        """
        copia = self.boleta_estado_pendente_de_informacao_de_cota_gerido()
        self.assertEqual(copia.estado, copia.ESTADO[2][0])
        # Verifica se a função cotizavel funciona
        self.assertFalse(copia.cotizavel())
        # Salvando o preço para disponibilizar o valor da cota no sistema.
        preco = mommy.make('mercado.Preco',
            ativo=copia.ativo,
            data_referencia=copia.data_cotizacao,
            preco_fechamento=decimal.Decimal('100.00').quantize(decimal.Decimal('1.000000'))
        )
        preco.full_clean()
        preco.save()
        # Verifica se a criação do preço muda o resultado da função cotizavel
        self.assertTrue(copia.cotizavel())
        # fechando a boleta em uma data que é diferente da data de cotizacao
        self.assertFalse(preco.data_referencia==preco.criado_em)
        data_fechamento = preco.criado_em.date()
        # Verificando se a boleta criou a boleta de passivo sem preco
        self.assertTrue(copia.boleta_passivo.all().exists())
        # Pegando a boleta de CPR de cotização.
        passivo = bm.BoletaPassivo.objects.get(object_id=copia.id)
        self.assertEqual(passivo.cota, None)

        copia.fechar_boleta(data_referencia=data_fechamento)

        passivo = bm.BoletaPassivo.objects.get(object_id=copia.id)

        self.assertEqual(passivo.valor, copia.financeiro)
        self.assertEqual(passivo.operacao, copia.operacao)
        self.assertEqual(passivo.data_movimentacao, copia.data_operacao)
        self.assertEqual(passivo.data_cotizacao, copia.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, copia.data_liquidacao)
        self.assertEqual(passivo.fundo, copia.ativo.gestao)
        self.assertEqual(passivo.cota, copia.preco)
        self.assertEqual(passivo.content_object, copia)

    def test_fechamento_transacao_7(self):
        """
        Transição 7 - Pendente de cotização e liquidação -> pendente de liquidação e informação de cotização.
            Condições necessárias:
                - Informação da cota indisponível na data de cotização
                - Boleta sem preço e quantidade.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Criação de uma boleta de CPR de cotização sem data de pagamento
                definida e data de início igual à data de cotização.
                - Criação de uma boleta de CPR de liquidação, com valor financeiro
                contrário à boleta de cotização, data inicial igual à data de
                cotização, e data de pagamento igual à data de liquidação.
                - Criação de uma provisão.
                - Atualizar estado.
        """
        # Removendo informações para caracterizar uma boleta sem informações
        # de cotização.
        boleta = self.boleta_ativo_qualquer
        boleta.id = None
        boleta.preco = None
        boleta.quantidade = None
        boleta.save()

        # Checando que não há boleta de CPR ou provisão criadas
        self.assertFalse(boleta.boleta_CPR.all().exists())
        self.assertFalse(boleta.boleta_provisao.all().exists())
        self.assertFalse(boleta.relacao_quantidade.all().exists())
        self.assertFalse(boleta.relacao_movimentacao.all().exists())

        boleta.fechar_boleta(boleta.data_cotizacao)

        tipo = ContentType.objects.get_for_model(boleta)

        # Checando se as boletas foram criadas
        self.assertEqual(boleta.boleta_CPR.all().count(), 2)

        cpr_cota = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=boleta.id, valor_cheio=boleta.financeiro)

        self.assertEqual(cpr_cota.data_inicio, boleta.data_cotizacao)
        self.assertEqual(cpr_cota.data_pagamento, None)
        self.assertEqual(cpr_cota.fundo, boleta.fundo)
        self.assertEqual(cpr_cota.valor_cheio, boleta.financeiro)

        cpr_liq = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=boleta.id, valor_cheio=-boleta.financeiro)

        self.assertEqual(cpr_liq.data_inicio, boleta.data_cotizacao)
        self.assertEqual(cpr_liq.data_pagamento, boleta.data_liquidacao)
        self.assertEqual(cpr_liq.fundo, boleta.fundo)
        self.assertEqual(cpr_liq.valor_cheio, -boleta.financeiro)

        self.assertTrue(boleta.boleta_provisao.all().exists())

        prov = bm.BoletaProvisao.objects.get(content_type__pk=tipo.id, object_id=boleta.id)

        self.assertEqual(prov.caixa_alvo, boleta.caixa_alvo)
        self.assertEqual(prov.fundo, boleta.fundo)
        self.assertEqual(prov.financeiro, -boleta.financeiro)

        self.assertFalse(boleta.relacao_quantidade.all().exists())
        self.assertFalse(boleta.relacao_movimentacao.all().exists())
        self.assertEqual(boleta.estado, boleta.ESTADO[3][0])

    def test_fechamento_transacao_7_ativo_gerido(self):
        """
        Transição 7 - Pendente de cotização e liquidação -> pendente de liquidação e informação de cotização.
            Condições necessárias:
                - Informação da cota indisponível na data de cotização
                - Boleta sem preço e quantidade.
                - Fechamento na data de cotização.
            Tarefas a executar:
                - Criação de uma boleta de CPR de cotização sem data de pagamento
                definida e data de início igual à data de cotização.
                - Criação de uma boleta de CPR de liquidação, com valor financeiro
                contrário à boleta de cotização, data inicial igual à data de
                cotização, e data de pagamento igual à data de liquidação.
                - Criação de uma provisão.
                - Atualizar estado.
        """
        # Removendo informações para caracterizar uma boleta sem informações
        # de cotização.
        boleta = self.boleta_ativo_gerido
        boleta.id = None
        boleta.preco = None
        boleta.quantidade = None
        boleta.save()

        # Checando que não há boleta de passivo
        self.assertFalse(boleta.boleta_passivo.all().exists())

        boleta.fechar_boleta(boleta.data_cotizacao)

        self.assertTrue(boleta.boleta_passivo.all().exists())

        passivo = bm.BoletaPassivo.objects.get(object_id=boleta.id)

        self.assertEqual(passivo.valor, boleta.financeiro)
        self.assertEqual(passivo.operacao, boleta.operacao)
        self.assertEqual(passivo.data_movimentacao, boleta.data_operacao)
        self.assertEqual(passivo.data_cotizacao, boleta.data_cotizacao)
        self.assertEqual(passivo.data_liquidacao, boleta.data_liquidacao)
        self.assertEqual(passivo.fundo, boleta.ativo.gestao)
        self.assertEqual(passivo.content_object, boleta)

    def test_fechamento_transacao_8(self):
        """
        Transição 8 - Pendente de liquidação e informação de cotização -> concluído.
            Condições necessárias:
                - Fechamento na data de liquidação;
                - Cota disponível na data de liquidação.
            Tarefas a executar:
                - Atualização da data de pagamento da boleta de CPR com a data
                de fechamento da cota no sistema.
                - Criação da movimentação e quantidade do ativo.
                - Atualzar estado.
        """
        boleta = self.boleta_estado_pendente_de_liquidacao_e_informacao_cota()
        # disponibilizando preço
        preco = mommy.make('mercado.preco',
            ativo=boleta.ativo,
            data_referencia=boleta.data_cotizacao,
            preco_fechamento=decimal.Decimal('1200').quantize(decimal.Decimal('1.000000'))
        )
        preco.full_clean()
        preco.save()

        self.assertEqual(boleta.boleta_CPR.all().count(), 2)
        self.assertFalse(boleta.relacao_quantidade.all().exists())
        self.assertFalse(boleta.relacao_movimentacao.all().exists())

        boleta.fechar_boleta(boleta.data_liquidacao)

        tipo = ContentType.objects.get_for_model(boleta)

        cpr_cota = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=boleta.id, valor_cheio=boleta.financeiro)

        # Verificando se a boleta foi atualizada.
        self.assertEqual(cpr_cota.data_pagamento, boleta.data_liquidacao)
        self.assertEqual(boleta.estado, boleta.ESTADO[5][0])
        self.assertTrue(boleta.relacao_quantidade.all().exists())
        self.assertTrue(boleta.relacao_movimentacao.all().exists())

    def test_fechamento_transacao_8_ativo_gerido(self):
        """
        Transição 8 - Pendente de liquidação e informação de cotização -> concluído.
            Condições necessárias:
                - Fechamento na data de liquidação;
                - Cota disponível na data de liquidação.
            Tarefas a executar:
                - Atualização da data de pagamento da boleta de CPR com a data
                de fechamento da cota no sistema.
                - Criação da movimentação e quantidade do ativo.
                - Atualzar estado.
                - Atualizar valor da cota na boleta de passivo
        """
        boleta = self.boleta_estado_pendente_de_liquidacao_e_informacao_cota_ativo_gerido()
        # disponibilizando preço
        preco = mommy.make('mercado.preco',
            ativo=boleta.ativo,
            data_referencia=boleta.data_cotizacao,
            preco_fechamento=decimal.Decimal('1200').quantize(decimal.Decimal('1.000000'))
        )
        preco.full_clean()
        preco.save()

        passivo = bm.BoletaPassivo.objects.get(object_id=boleta.id)

        self.assertEqual(boleta.boleta_CPR.all().count(), 2)
        self.assertTrue(boleta.boleta_passivo.all().exists())
        boleta.fechar_boleta(boleta.data_liquidacao)

        passivo = bm.BoletaPassivo.objects.get(object_id=boleta.id)

        # Verificando se a boleta foi atualizada.
        self.assertEqual(boleta.estado, boleta.ESTADO[5][0])
        self.assertEqual(passivo.cota, boleta.preco)

    def test_fechamento_transacao_9(self):
        """
        Transição 9 - Pendente de liquidação e informação de cotização -> Pendente de informação de cotização.
            Condições necessárias:
                - Fechamento na data de liquidação
                - Cota indisponível na data de liquidação.
            Tarefas a executar:
                - Apenas atualiza o estado.
        """
        boleta = self.boleta_estado_pendente_de_liquidacao_e_informacao_cota()
        self.assertFalse(boleta.cotizavel())
        boleta.fechar_boleta(boleta.data_liquidacao)
        self.assertEqual(boleta.estado, boleta.ESTADO[2][0])

        tipo = ContentType.objects.get_for_model(boleta)
        cpr_cota = bm.BoletaCPR.objects.get(content_type__pk=tipo.id, object_id=boleta.id, valor_cheio=boleta.financeiro)
        self.assertEqual(cpr_cota.data_pagamento, None)

    def boleta_estado_pendente_de_cotizacao(self):
        """
        Método auxiliar para colocar uma boleta no estado "Pendente de cotização."
        """
        copia = self.boleta_ativo_qualquer
        copia.id = None
        copia.data_liquidacao = datetime.date(year=2018, month=10, day=16)
        copia.data_cotizacao = datetime.date(year=2018, month=10, day=19)
        data_fechamento = copia.data_liquidacao
        copia.preco = None
        copia.quantidade = None
        copia.save()
        copia.fechar_boleta(data_referencia=data_fechamento)
        return copia

    def boleta_estado_pendente_de_cotizacao_ativo_gerido(self):
        """
        Método auxiliar para colocar uma boleta no estado "Pendente de cotização."
        """
        copia = self.boleta_ativo_gerido
        copia.id = None
        copia.data_liquidacao = datetime.date(year=2018, month=10, day=16)
        copia.data_cotizacao = datetime.date(year=2018, month=10, day=19)
        data_fechamento = copia.data_liquidacao
        copia.preco = None
        copia.quantidade = None
        copia.save()
        copia.fechar_boleta(data_referencia=data_fechamento)
        return copia

    def boleta_estado_pendente_de_liquidacao(self):
        """
        Método auxiliar para colocar uma boleta no estado "Pendente de liquidação."
        """
        copia = self.boleta_ativo_qualquer
        copia.id = None
        data_fechamento = copia.data_cotizacao
        copia.estado = copia.ESTADO[4][0]
        copia.save()
        copia.fechar_boleta(data_referencia=data_fechamento)

        return copia

    def boleta_estado_pendente_de_liquidacao_ativo_gerido(self):
        """
        Método auxiliar para colocar uma boleta no estado "Pendente de liquidação."
        """
        copia = self.boleta_ativo_gerido
        copia.id = None
        data_fechamento = copia.data_cotizacao
        copia.estado = copia.ESTADO[4][0]
        copia.save()
        copia.fechar_boleta(data_referencia=data_fechamento)

        return copia

    def boleta_estado_pendente_de_informacao_de_cota(self):
        """
        Método auxiliar para colocar uma boleta no estado "Pendente de informação de cotizacao."
        """
        copia = self.boleta_estado_pendente_de_cotizacao()
        copia.fechar_boleta(copia.data_cotizacao)
        return copia

    def boleta_estado_pendente_de_informacao_de_cota_gerido(self):
        """
        Método auxiliar para colocar uma boleta no estado "Pendente de informação de cotizacao."
        """
        copia = self.boleta_estado_pendente_de_cotizacao_ativo_gerido()
        copia.fechar_boleta(copia.data_cotizacao)
        return copia

    def boleta_estado_pendente_de_liquidacao_e_informacao_cota(self):
        """
        Cria e retorna uma boleta com o estado pendente de liquidação e
        informação de cota
        """
        boleta = self.boleta_ativo_qualquer
        boleta.id = None
        boleta.preco = None
        boleta.quantidade = None
        boleta.save()
        boleta.fechar_boleta(boleta.data_cotizacao)
        return boleta

    def boleta_estado_pendente_de_liquidacao_e_informacao_cota_ativo_gerido(self):
        """
        Cria e retorna uma boleta com o estado pendente de liquidação e
        informação de cota
        """
        boleta = self.boleta_ativo_gerido
        boleta.id = None
        boleta.preco = None
        boleta.quantidade = None
        boleta.save()
        boleta.fechar_boleta(boleta.data_cotizacao)
        return boleta

class BoletaPassivoUnitTests(TestCase):
    """
    Classe de unit tests de Passivo
    """
    # Teste - Em caso de aporte - criar certificado de passivo.
    # Teste - Em caso de resgate - consumir certificado de passivo.
    # Teste - Criação de boleta de provisão
    # Teste - Criação da boleta de CPR
    def setUp(self):
        self.cotista = mommy.make('fundo.cotista',
            nome='Atena'
        )
        self.fundo = mommy.make('fundo.Fundo',
            nome='Veredas'
        )
        # Boleta que faz aplicação - cria 1.000 cotas, valor de 1.000.000
        self.boleta_aplicacao = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2018, month=10, day=26),
            data_cotizacao=datetime.date(year=2018, month=10, day=27),
            data_liquidacao=datetime.date(year=2018, month=10, day=26),
            cota=decimal.Decimal('1000'),
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )
        # Boleta que faz aplicação - cria 1.000 cotas, valor de 1.000.000
        self.boleta_aplicacao_2016 = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2016, month=10, day=26),
            data_cotizacao=datetime.date(year=2016, month=10, day=27),
            data_liquidacao=datetime.date(year=2016, month=10, day=26),
            cota=decimal.Decimal('1000'),
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )
        # Boleta que faz aplicação - cria 500 cotas, valor de 1.000.000
        self.boleta_aplicacao_2017 = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2017, month=10, day=26),
            data_cotizacao=datetime.date(year=2017, month=10, day=27),
            data_liquidacao=datetime.date(year=2017, month=10, day=26),
            cota=decimal.Decimal('2000'),
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )
        self.boleta_aplicacao_cotizacao_antes_da_liquidacao = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2018, month=10, day=26),
            data_cotizacao=datetime.date(year=2018, month=10, day=27),
            data_liquidacao=datetime.date(year=2018, month=10, day=28),
            cota=decimal.Decimal('1000'),
            operacao=bm.BoletaPassivo.OPERACAO[0][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )
        # Boleta que faz resgate
        self.boleta_resgate = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2018, month=10, day=26),
            data_cotizacao=datetime.date(year=2018, month=10, day=27),
            data_liquidacao=datetime.date(year=2018, month=10, day=26),
            cota=decimal.Decimal('1000'),
            operacao=bm.BoletaPassivo.OPERACAO[1][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )
        self.boleta_resgate_cotizacao_antes_da_liquidacao = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2018, month=10, day=26),
            data_cotizacao=datetime.date(year=2018, month=10, day=27),
            data_liquidacao=datetime.date(year=2018, month=10, day=28),
            cota=decimal.Decimal('1000'),
            operacao=bm.BoletaPassivo.OPERACAO[1][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )
        # TODO: teste de resgate total
        # Boleta que faz resgate total
        self.boleta_resgate_total = mommy.make('boletagem.BoletaPassivo',
            cotista=self.cotista,
            data_movimentacao=datetime.date(year=2018, month=10, day=26),
            data_cotizacao=datetime.date(year=2018, month=10, day=27),
            data_liquidacao=datetime.date(year=2018, month=10, day=26),
            cota=decimal.Decimal('1000'),
            operacao=bm.BoletaPassivo.OPERACAO[2][0],
            valor=decimal.Decimal('1000000').quantize(decimal.Decimal('1.00')),
            fundo=self.fundo
        )

    def test_criar_provisao_aplicacao(self):
        """
        Testa a criação de boleta de provisão do fundo investido.
        """
        copia = self.boleta_aplicacao
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.boleta_provisao.all().exists())
        copia.criar_provisao()
        self.assertTrue(copia.boleta_provisao.all().exists())

        provisao = bm.BoletaProvisao.objects.get(object_id=copia.id)

        self.assertEqual(abs(copia.valor), provisao.financeiro)
        self.assertEqual(copia.fundo.caixa_padrao, provisao.caixa_alvo)
        self.assertEqual(copia.data_liquidacao, provisao.data_pagamento)
        self.assertEqual(copia.fundo, provisao.fundo)
        self.assertEqual(copia, provisao.content_object)

    def test_criar_provisao_resgate(self):
        """
        Testa a criação de boleta de provisão do fundo investido de acordo com
        a operação.
        """
        copia = self.boleta_resgate
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.boleta_provisao.all().exists())
        copia.criar_provisao()
        self.assertTrue(copia.boleta_provisao.all().exists())

        provisao = bm.BoletaProvisao.objects.get(object_id=copia.id)

        self.assertEqual(-abs(copia.valor), provisao.financeiro)
        self.assertEqual(copia.fundo.caixa_padrao, provisao.caixa_alvo)
        self.assertEqual(copia.data_liquidacao, provisao.data_pagamento)
        self.assertEqual(copia.fundo, provisao.fundo)
        self.assertEqual(copia, provisao.content_object)

    def test_criar_boleta_CPR_aplicacao_liquidacao_antes_da_cotizacao(self):
        """
        Testa criação da boleta de CPR equivalente à movimentação.
        """
        copia = self.boleta_aplicacao
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())

        cpr = bm.BoletaCPR.objects.get(object_id=copia.id)

        self.assertEqual(-abs(copia.valor), cpr.valor_cheio)
        self.assertEqual(copia.fundo, cpr.fundo)
        self.assertEqual(copia.data_liquidacao, cpr.data_inicio)
        self.assertEqual(copia.data_cotizacao, cpr.data_pagamento)
        self.assertEqual(cpr.data_vigencia_fim, None)
        self.assertEqual(cpr.data_vigencia_inicio, None)
        self.assertEqual(cpr.tipo, bm.BoletaCPR.TIPO[2][0])
        self.assertEqual(cpr.capitalizacao, bm.BoletaCPR.CAPITALIZACAO[2][0])

    def test_criar_boleta_CPR_aplicacao_cotizacao_antes_da_liquidacao(self):
        """
        Testa criação da boleta de CPR equivalente à movimentação.
        """
        copia = self.boleta_aplicacao_cotizacao_antes_da_liquidacao
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())

        cpr = bm.BoletaCPR.objects.get(object_id=copia.id)

        self.assertEqual(abs(copia.valor), cpr.valor_cheio)
        self.assertEqual(copia.fundo, cpr.fundo)
        self.assertEqual(copia.data_cotizacao, cpr.data_inicio)
        self.assertEqual(copia.data_liquidacao, cpr.data_pagamento)
        self.assertEqual(cpr.data_vigencia_fim, None)
        self.assertEqual(cpr.data_vigencia_inicio, None)
        self.assertEqual(cpr.tipo, bm.BoletaCPR.TIPO[2][0])
        self.assertEqual(cpr.capitalizacao, bm.BoletaCPR.CAPITALIZACAO[2][0])

    def test_criar_boleta_CPR_resgate_liquidacao_antes_da_cotizacao(self):
        """
        Testa criação da boleta de CPR equivalente à movimentação.
        """
        copia = self.boleta_resgate
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())

        cpr = bm.BoletaCPR.objects.get(object_id=copia.id)

        self.assertEqual(abs(copia.valor), cpr.valor_cheio)
        self.assertEqual(copia.fundo, cpr.fundo)
        self.assertEqual(copia.data_liquidacao, cpr.data_inicio)
        self.assertEqual(copia.data_cotizacao, cpr.data_pagamento)
        self.assertEqual(cpr.data_vigencia_fim, None)
        self.assertEqual(cpr.data_vigencia_inicio, None)
        self.assertEqual(cpr.tipo, bm.BoletaCPR.TIPO[2][0])
        self.assertEqual(cpr.capitalizacao, bm.BoletaCPR.CAPITALIZACAO[2][0])

    def test_criar_boleta_CPR_resgate_cotizacao_antes_da_liquidacao(self):
        """
        Testa criação da boleta de CPR equivalente à movimentação.
        """
        copia = self.boleta_resgate_cotizacao_antes_da_liquidacao
        copia.id = None
        copia.full_clean()
        copia.save()

        self.assertFalse(copia.boleta_CPR.all().exists())
        copia.criar_boleta_CPR()
        self.assertTrue(copia.boleta_CPR.all().exists())

        cpr = bm.BoletaCPR.objects.get(object_id=copia.id)

        self.assertEqual(-abs(copia.valor), cpr.valor_cheio)
        self.assertEqual(copia.fundo, cpr.fundo)
        self.assertEqual(copia.data_cotizacao, cpr.data_inicio)
        self.assertEqual(copia.data_liquidacao, cpr.data_pagamento)
        self.assertEqual(cpr.data_vigencia_fim, None)
        self.assertEqual(cpr.data_vigencia_inicio, None)
        self.assertEqual(cpr.tipo, bm.BoletaCPR.TIPO[2][0])
        self.assertEqual(cpr.capitalizacao, bm.BoletaCPR.CAPITALIZACAO[2][0])

    def test_criar_certificado_aplicacao(self):
        """
        Testa a criação do certificado de aplicação da boleta.
        """
        copia = self.boleta_aplicacao
        copia.id = None
        copia.save()

        self.assertFalse(copia.certificado_passivo.all().exists())
        copia.gerar_certificado()
        self.assertTrue(copia.certificado_passivo.all().exists())

        certificado = copia.certificado_passivo.get(boletapassivo=copia)

        self.assertEqual(certificado.cotista, copia.cotista)
        self.assertEqual(certificado.qtd_cotas, (copia.valor/copia.cota).quantize(decimal.Decimal('1.0000000')))
        self.assertEqual(certificado.valor_cota, copia.cota)
        self.assertEqual(certificado.cotas_aplicadas, (copia.valor/copia.cota).quantize(decimal.Decimal('1.0000000')))
        self.assertEqual(certificado.data, copia.data_cotizacao)

    def test_consumir_certificado_parcial_resgate(self):
        """
        Testa o consumo parcial de um certificado de passivo do fundo. A boleta
        deve consumir apenas o certificado de 2016.
        Quantidade de cotas total a ser consumida = Financeiro/Cota
        """
        # Criando certificados de aplicacao
        aplicacao_2016 = self.boleta_aplicacao_2016
        aplicacao_2016.id = None
        aplicacao_2016.save()
        aplicacao_2016.gerar_certificado()

        aplicacao_2017 = self.boleta_aplicacao_2017
        aplicacao_2017.id = None
        aplicacao_2017.save()
        aplicacao_2017.gerar_certificado()

        certificado_consumido = aplicacao_2016.certificado_passivo.get(boletapassivo=aplicacao_2016)
        certificado_intacto = aplicacao_2017.certificado_passivo.get(boletapassivo=aplicacao_2017)
        # Quantidade de cotas original no certificado.
        qtd_original = certificado_consumido.cotas_aplicadas

        copia = self.boleta_resgate
        copia.id = None
        copia.save()

        self.assertFalse(copia.certificado_passivo.all().exists())
        copia.consumir_certificado()
        self.assertTrue(copia.certificado_passivo.all().exists())

        certificado = copia.certificado_passivo.get(boletapassivo=copia)

        self.assertEqual(certificado.id, certificado_consumido.id)
        self.assertEqual(certificado.cotas_aplicadas, (qtd_original
            - copia.valor/copia.cota).quantize(decimal.Decimal('1.0000000')))

    def test_consumir_dois_certificados_resgate(self):
        """
        Quando resgates consomem mais de uma boleta, a quantidade deve se
        distribuir entre vários certificados, por ordem de mais antiga primeiro.
        """
        # Criando certificados de aplicacao
        aplicacao_2016 = self.boleta_aplicacao_2016
        aplicacao_2016.id = None
        aplicacao_2016.save()
        # 1.000 cotas
        aplicacao_2016.gerar_certificado()
        # 500 cotas
        aplicacao_2017 = self.boleta_aplicacao_2017
        aplicacao_2017.id = None
        aplicacao_2017.save()
        aplicacao_2017.gerar_certificado()

        certificado_consumido = aplicacao_2016.certificado_passivo.get(boletapassivo=aplicacao_2016)
        certificado_consumido_parcial = aplicacao_2017.certificado_passivo.get(boletapassivo=aplicacao_2017)
        # Quantidade de cotas original no certificado totalmente consumido
        qtd_certificado_consumida = certificado_consumido.cotas_aplicadas
        qtd_certificado_parcial = certificado_consumido_parcial.cotas_aplicadas

        copia = self.boleta_resgate
        copia.id = None
        # Resgate total de 1.200 cotas
        copia.valor = decimal.Decimal('3000000')
        copia.cota = decimal.Decimal('2500')
        qtd_cotas_total_consumida = (copia.valor/copia.cota).quantize(decimal.Decimal('1.0000000'))
        copia.save()

        self.assertFalse(copia.certificado_passivo.all().exists())
        copia.consumir_certificado()
        self.assertTrue(copia.certificado_passivo.all().exists())
        self.assertEqual(copia.certificado_passivo.all().count(), 2)

        certificado_liquidado = copia.certificado_passivo.filter(boletapassivo=copia).earliest('data')
        certificado_parcial = copia.certificado_passivo.filter(boletapassivo=copia).latest('data')

        self.assertEqual(certificado_liquidado.id, certificado_consumido.id)
        # Todas as cotas foram consumidas
        self.assertEqual(certificado_liquidado.cotas_aplicadas, decimal.Decimal('0'))

        self.assertEqual(certificado_parcial.id, certificado_consumido_parcial.id)
        # Consome as cotas que sobraram
        self.assertEqual(certificado_parcial.cotas_aplicadas, qtd_certificado_parcial - (qtd_cotas_total_consumida - qtd_certificado_consumida))
