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
            data_vencimento='2018-10-24',
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
            data_reversao=datetime.date(year=2018, month=10, day=5),
            data_vencimento=datetime.date(year=2018, month=12, day=25),
            quantidade=15000,
            preco=decimal.Decimal(10),
            taxa=decimal.Decimal(0.15),
            reversivel=True)
        self.boleta_vencimento_errado = mommy.make('boletagem.BoletaEmprestimo',
            data_vencimento=datetime.date(year=2018, month=10, day=1),
            data_operacao=datetime.date(year=2018, month=10, day=3))
        self.boleta_liquidacao_anterior_operacao = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=1),
            data_operacao=datetime.date(year=2018, month=10, day=3),
            data_vencimento=datetime.date(year=2018, month=10, day=24))
        self.boleta_liquidacao_posterior_vencimento = mommy.make('boletagem.BoletaEmprestimo',
            data_vencimento=datetime.date(year=2018, month=10, day=1),
            data_liquidacao=datetime.date(year=2018, month=10, day=13))
        self.boleta_liquidacao_anterior_reversivel = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=1),
            data_reversao=datetime.date(year=2018, month=10, day=3),
            data_vencimento=datetime.date(year=2018, month=10, day=20))
        self.boleta_correta = mommy.make('boletagem.BoletaEmprestimo',
            data_liquidacao=datetime.date(year=2018, month=10, day=25),
            reversivel=False,
            data_vencimento=datetime.date(year=2018, month=10, day=30),
            data_operacao=datetime.date(year=2018, month=10, day=1),
            quantidade=1000,
            taxa=0.2,
            preco=10)
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
            preco=10)

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

class BoletaRendaFixaLocalUnitTest(TestCase):
    """
    Classe de Unit Test de BoletaRendaFixaLocal
    """
    def setUp(self):
        self.boleta = mommy.make('boletagem.BoletaRendaFixaLocal',
            data_operacao=datetime.date(year=2018, month=10, day=8),
            data_liquidacao=datetime.date(year=2018, month=10, day=9),
            operacao='C',
            quantidade=1000,
            preco=decimal.Decimal(9733.787491),
            taxa=6.4
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

class BoletaFundoLocalUnitTest(TestCase):
    """
    Classe de Unit Test de BoletaFundoLocal
    """
    def setUp(self):
        self.boleta = mommy.make('boletagem.BoletaFundoLocal',
            data_operacao=datetime.date(year=2018, month=10, day=15),
            data_cotizacao=datetime.date(year=2018, month=10, day=16),
            data_liquidacao=datetime.date(year=2018, month=10, day=16),
            operacao="Aplicação",
            quantidade=1000,
            preco=1300
            )

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

    @pytest.mark.xfail
    def test_cria_quantidade(self):
        """
        Testa se a boleta cria quantidades corretamente.
        """
