"""
Modelos deste app são voltados para a gravação de operações e inserção de
eventos no sistema.
Responsabilidades deste app:
    - Processamento de input de informações de mercado.
    - Repasse de informações aos apps responsáveis pelas informações
    processadas.

Funcionamento:
    - Boletas de ativos geram Movimentações e Quantidades dos seus respectivos
    ativos no app de Fundo. Movimentações e Quantidades são consolidados em
    Vértices, que compõem uma Carteira. No fechamento de boletas de
    ativos, são geradas boletas de CPR e provisão, para refletir o CPR
    do ativo e a movimentação de caixa causada pela operação com o ativo.
    - Boletas de CPR geram CPRs, que, por sua vez, geram Movimentações e
    Quantidades.
    - Boletas de Provisão criam as Movimentações e Quantidades de caixas
    dos fundos.
    - Boletas de preço servem para inserirmos no sistema informações sobre
    preços de ativos. Preços podem ser dividios entre preço de fechamento de
    mercado, preço contábil, estimativa de preço, preço gerencial. Pode ser
    que, futuramente, haja a necessidade de armazenamento de mais tipos
    diferentes de preço. Os preços são armazenados no app Mercado.
    - Boletas de proventos servem para armazenar informações sobre proventos
    anunciados de ativos. Os proventos são armazenados no app Mercado.
    No fechamento da boleta de proventos, as carteiras são consultadas para
    ver se o ativo faz parte delas. Caso faça parte, a boleta de provento
    gera uma boleta de provisão e uma boleta de CPR, assim como uma
    Movimentação do ativo.
"""
import datetime
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from fundo.models import Quantidade, Movimentacao
import ativos.models

# Create your models here.

class BoletaAcao(models.Model):
    """
    Representa a boleta de um trade de ações. Ao fazer o fechamento de um dia
    de um fundo, as boletas de ação do dia são processadas para gerar a boleta
    de provisão (esta gerará a movimentação e quantidade de caixa) e a
    movimentação do ativo.
    """
    OPERACAO = (
        ('C', 'C'),
        ('V', 'V')
    )

    acao = models.ForeignKey("ativos.Acao", on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today, null=False)
    data_liquidacao = models.DateField(null=False)
    corretora = models.ForeignKey("fundo.Corretora", null=False, on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.IntegerField()
    preco = models.DecimalField(max_digits=13, decimal_places=7)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_acao')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_acao')

    class Meta:
        verbose_name_plural = "Boletas de operação de ações"

    def __str__(self):
        return "Operação de %s executada em %s." % (self.acao, self.data_operacao)

    def fechar_boleta(self):
        """
        Função para fazer o fechamento de uma boleta. O fechamento de uma boleta
        faz com que ela crie as boletas de provisão, boletas de CPR,
        quantidade e movimentações do ativo correspondente.
        """
        self.criar_boleta_provisao()
        self.criar_boleta_CPR()
        self.criar_quantidade()
        self.criar_movimentacao()

    def criar_boleta_provisao(self):
        """
        Cria uma boleta de provisão de acordo com os parâmeteros da boleta
        de ação. Se já houver uma boleta de provisão criada, não há necessidade
        de criar outra.
        """
        # Checar se já há boleta de provisão criada relacionada com esta.
        if self.boleta_provisao.all().exists() == False:
            # Criar boleta de provisão
            boleta_provisao = BoletaProvisao(
                caixa_alvo = self.caixa_alvo,
                fundo = self.fundo,
                data_pagamento = self.data_liquidacao,
                # A movimentação de caixa tem sinal oposto à variação de quantidade
                financeiro = - (self.preco * self.quantidade),
                content_object = self
            )
            boleta_provisao.save()

    def criar_boleta_CPR(self):
        """
        Cria uma boleta de CPR de acordo com os parâmeteros da boleta
        de ação. Se já houver uma boleta de CPR criada, não há necessidade
        de criar outra.
        """
        # Checar se há boleta de CPR já criada:
        if self.boleta_CPR.all().exists() == False:
            # Criar boleta de CPR
            op = ''
            if self.operacao == "C":
                op = 'Compra '
            else:
                op = 'Venda '
            boleta_CPR = BoletaCPR(
                descricao = op + self.acao.nome,
                valor_cheio = -(self.preco * self.quantidade),
                data_inicio = self.data_operacao,
                data_pagamento = self.data_liquidacao,
                content_object = self
            )
            boleta_CPR.save()

    def criar_quantidade(self):
        """
        Cria uma quantidade do ativo de acordo com os parâmeteros da boleta
        de ação. Se já houver uma quantidade criada, não há necessidade
        de criar outra.
        """
        # Checar se há quantidade já criada
        if self.relacao_quantidade.all().exists() == False:
            # Criar Quantidade do Ativo
            acao_quantidade = Quantidade(
                qtd = self.quantidade,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self
            )
            acao_quantidade.save()

    def criar_movimentacao(self):
        """
        Cria uma movimentação de acordo com os parâmeteros da boleta
        de ação. Se já houver uma movimentação criada, não há necessidade
        de criar outra.
        """
        # Checar se há movimentação já criada
        if self.relacao_movimentacao.all().exists() == False:
            # Criar Movimentacao do Ativo
            acao_movimentacao = Movimentacao(
                valor = self.preco * self.quantidade,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self
            )
            acao_movimentacao.save()

class BoletaRendaFixaLocal(models.Model):
    """
    Representa uma boleta de renda fixa local. Processada da mesma maneira que
    a boleta de ação
    """
    OPERACAO = (
        ('C', 'C'),
        ('V', 'V')
    )

    ativo = models.ForeignKey("ativos.Renda_Fixa", on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today, null=False)
    data_liquidacao = models.DateField(default=datetime.date.today, null=False)
    corretora = models.ForeignKey('fundo.Corretora', null=False, on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco = models.DecimalField(max_digits=13, decimal_places=6)
    taxa = models.DecimalField(max_digits=6, decimal_places=4)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_rfloc')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_rfloc')

class BoletaRendaFixaOffshore(models.Model):
    """
    Representa uma operação de renda fixa offshore. Processado da mesma maneira
    que a boleta de ação.
    """
    OPERACAO = (
        ('C', 'C'),
        ('V', 'V')
    )
    ativo = models.ForeignKey("ativos.Renda_Fixa", on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today, null=False)
    data_liquidacao = models.DateField(default=datetime.date.today, null=False)
    corretora = models.ForeignKey('fundo.Corretora', null=False, on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    nominal = models.DecimalField(max_digits=13, decimal_places=6)
    taxa = models.DecimalField(max_digits=6, decimal_places=4)
    preco = models.DecimalField(max_digits=10, decimal_places=8)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_rfoff')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_rfoff')

class BoletaFundoLocal(models.Model):
    """
    Representa uma operação de cotas de fundo local. Processado da mesma maneira
    que a boleta de ação.
    """
    OPERACAO = (
        ('Aplicação', 'Aplicação'),
        ('Resgate', 'Resgate'),
        ('Resgate Total', 'Resgate Total')
    )
    TIPO_LIQUIDACAO = (
        ('Interna', 'Interna'),
        ('Transferência', 'Transferência'),
        ('CETIP', 'CETIP')
    )

    ativo = models.ForeignKey('ativos.Fundo_Local', on_delete=models.PROTECT)
    data_operacao = models.DateField(null=False, default=datetime.date.today)
    data_cotizacao = models.DateField()
    data_liquidacao = models.DateField()
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    operacao = models.CharField(max_length=13, choices=OPERACAO)
    liquidacao = models.CharField(max_length=13, choices=TIPO_LIQUIDACAO)
    financeiro = models.DecimalField(max_digits=16, decimal_places=6)
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_fundo_local')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_fundo_local')

class BoletaFundoOffshore(models.Model):
    """
    Representa uma operação de cotas de fundo offshore. Processado de acordo
    com o seu estado atual.
    """
    ESTADO = (
        ('Pendente de Cotização', 'Pendente de Cotização'),
        ('Pendente de Liquidação', 'Pendente de Liquidação'),
        ('Pendente de informação de Cotização', 'Pendente de informação de Cotização'),
        ('Pendente de Liquidação e informação de Cotização',
            'Pendente de Liquidação e informação de Cotização'),
        ('Pendente de Liquidação e Cotização','Pendente de Liquidação e Cotização'),
        ('Concluído', 'Concluído')
    )

    ativo = models.ForeignKey('ativos.Fundo_Offshore', on_delete=models.PROTECT)
    estado = models.CharField(max_length=48)
    data_operacao = models.DateField()
    data_cotizacao = models.DateField()
    data_liquidacao = models.DateField()

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_fundo_off')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_fundo_off')

class BoletaEmprestimo(models.Model):
    """
    Representa uma operação de empréstimo de ações locais.
    """
    OPERACAO = (
        ('Doador', 'Doador'),
        ('Tomador', 'Tomador'),
        ('Liquidação', 'Liquidação')
    )

    ativo = models.ForeignKey('ativos.Acao', on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    corretora = models.ForeignKey('fundo.Corretora', on_delete=models.PROTECT)
    data_vencimento = models.DateField()
    data_liquidacao = models.DateField()
    reversivel = models.BooleanField()
    data_reversao = models.DateField()
    operacao = models.CharField('Operação', max_length=10)
    comissao = models.DecimalField(max_digits=9, decimal_places=6)
    quantidade = models.DecimalField(max_digits=10, decimal_places=6)
    taxa = models.DecimalField(max_digits=8, decimal_places=6)
    preco = models.DecimalField(max_digits=10, decimal_places=6)
    boleta_original = models.ForeignKey('self', on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_emprestimo')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_emprestimo')

    def liquidacao_boleta(self, quantidade):
        """
        Uma liquidação gera uma movimentação negativa do
        ativo, para que a movimentação entre como um rendimento do ativo na
        avaliação do desempenho deste, sem alteração de quantidade do mesmo,
        e uma movimentação de entrada de caixa.
        Uma liquidação pode ser completa ou parcial. A liquidação completa
        implica apenas na criação da movimentação de caixa e do ativo. Na liquidação
        parcial, apenas uma parte das ações do contrato de aluguel são liquidadas.
        Isso separa a boleta em duas partes, a parte que foi liquidada e a parte
        que continua me vigência. A boleta original se torna a parte liquidada
        e uma nova boleta é criada para o restante das ações ainda alugadas.
        """

    def fechar_boleta(self):
        """
        O fechamento de uma boleta de empréstimo acumula o CPR de aluguel.
        Cria apenas uma quantidade.
        """

class BoletaCambio(models.Model):
    """
    Representa uma operação de câmbio entre caixas. Ele também pode ser
    usado para transferência de caixas da mesma moeda
    """
    # Fundo que fará o câmbio
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    # Pelo caixa origem, determinamos qual é a moeda origem
    caixa_origem = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT,
        related_name='related_caixa_origem')
    # Pelo caixa final, determinamos qual é a moeda final
    caixa_destino = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT,
        related_name='related_caixa_final')
    # taxa pelo qual o cambio foi feito:
    # caixa_final = caixa_origem * cambio
    cambio = models.DecimalField(max_digits=10, decimal_places=6)
    # Taxa paga para execução do cambio
    taxa = models.DecimalField(max_digits=8, decimal_places=2)
    # Valor financeiro do caixa de origem
    financeiro_origem = models.DecimalField(max_digits=16, decimal_places=6)
    # Valor financeiro do caixa de destino
    financeiro_final = models.DecimalField(max_digits=16, decimal_places=6)
    # Data em que ocorrerá liquidação no caixa origem
    data_liquidacao_origem = models.DateField(default=datetime.date.today)
    # Data em que ocorrerá liquidação no caixa final
    data_liquidacao_destino = models.DateField(default=datetime.date.today)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_cambio')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_cambio')

class BoletaProvisao(models.Model):
    """
    Boleta para registrar despesas a serem pagas por um fundo
    """

    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    data_pagamento = models.DateField()
    financeiro = models.DecimalField(max_digits=10, decimal_places=2)

    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_provisao')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_provisao')

    # Content type para servir de ForeignKey de qualquer boleta a ser
    # inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

class BoletaCPR(models.Model):
    """
    Boleta para registrar CPR dos fundos.
    """
    # Descrição sobre o que é o CPR.
    descricao = models.CharField("Descrição", max_length=50)
    # Valor cheio do CPR.
    valor_cheio = models.DecimalField(max_digits=12, decimal_places=2,
        blank=True, null=True)
    # Valor parcial do CPR, no caso de boletar CPR que acumula diariamente
    valor_parcial = models.DecimalField(max_digits=12, decimal_places=2,
        blank=True, null=True)
    # Data em que o CPR deve começar a ser considerado no fundo
    data_inicio = models.DateField()
    # Data de início da capitalização do CPR.
    data_vigencia_inicio = models.DateField(null=True, blank=True)
    # Data de fim da capitalização do CPR.
    data_vigencia_fim = models.DateField(null=True, blank=True)
    # Data em que o CPR deve sair da carteira.
    data_pagamento = models.DateField()

    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_cpr')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_cpr')

    # Content type para servir de ForeignKey de qualquer boleta de operação
    # a ser inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Boletas de CPR"

    def __str__(self):
        return '%s' % (self.descricao)

class BoletaPrecos(models.Model):
    """
    Boleta para registro de preços de ativos.
    """
    ativo = models.ForeignKey('ativos.Ativo', on_delete=models.PROTECT)
