"""
Modelos deste app servem para armazenar informações e processar eventos de
fundos geridos.
Responsabilidades deste app:
    - Executar funções relacionadas ao fundo:
        - Fechamento diário para cálculo de cota.
        - Fechamento mensal para cálculo de cota.
"""
import decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class BaseModelQuerySet(models.query.QuerySet):
    def delete(self):
        return super(BaseModelQuerySet, self).update(deletado_em=timezone.now())

    def hard_delete(self):
        return super(BaseModelQuerySet, self).delete()

    def alive(self):
        return self.filter(deletado_em=None)

    def dead(self):
        return self.exclude(deletado_em=None)

class BaseModelManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(BaseModelManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return BaseModelQuerySet(self.model).filter(deletado_em=None)
        return BaseModelQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class BaseModel(models.Model):
    """
    Classe base para criar campos comuns a todas as classes, como 'criado em'
    ou 'atualizado em'
    """
    deletado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = BaseModelManager()
    all_objects = BaseModelManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deletado_em = timezone.now()
        self.save()

    def hard_delete(self):
        super(BaseModel, self).delete()

class Fundo(BaseModel):
    """
    Descreve informações relevantes para um fundo.

    """
    # Categorias do fundo.
    CATEGORIAS = (
        ("Fundo de Ações", "Fundo de Ações"),
        ("Fundo Multimercado", "Fundo Multimercado"),
        ("Fundo Imobiliário", "Fundo Imobiliário"),
        ("Fundo de Renda Fixa", "Fundo de Renda Fixa")
    )
    CAPITALIZACAO = (
        ("Diária","Diária"),
        ("Mensal","Mensal")
    )
    # Nome do Fundo.
    nome = models.CharField(max_length=100, unique=True)
    # Instituição que faz a administração do fundo.
    administradora = models.ForeignKey("Administradora", on_delete=models.PROTECT)
    # Instituição que faz a gestão do fundo.
    gestora = models.ForeignKey('Gestora', on_delete=models.PROTECT, null=True,
        blank=True)
    # Instituição que distribui o fundo (capta investimentos no fundo)
    distribuidora = models.ForeignKey("Distribuidora", on_delete=models.PROTECT,
        null=True, blank=True)
    # Instituição que faz a custódia das cotas do fundo.
    custodia = models.ForeignKey("Custodiante", on_delete=models.PROTECT,
        null=True, blank=True)
    # Tipo de fundo - Ações, Renda Fixa, Imobiliário, etc... Importante
    # para determinação da metodologia de cálculo do IR.
    categoria = models.CharField("Categoria do Fundo", max_length=40,
        null=True, blank=True, choices=CATEGORIAS)
    # Data de constituição do fundo
    data_de_inicio = models.DateField(null=True, blank=True)
    # País em que o fundo é administrado. Indiretamente indica a moeda que
    # o PL é calculado
    pais = models.ForeignKey('ativos.Pais', on_delete=models.PROTECT)
    # Porcentagem que incide sobre o PL do fundo para taxa de administração.
    # O número é dado em porcentagem - se taxa_administracao = 0,1, a taxa
    # que incide sobre o PL é de 0,1%
    taxa_administracao = models.DecimalField('Taxa de Administração',
        max_digits=7, decimal_places=5, null=True, blank=True)
    # Indica de quanto em quanto tempo a taxa de administração é apurada
    # No caso dos fundos locais, como a carteira é diária, a taxa de
    # administração é acumulada diariamente, com base no PL do dia anterior.
    # No caso de fundos offshore, com carteiras mensais, a taxa é calculada
    # mensalmente, com base no PL de fim do mês.
    capitalizacao_taxa_adm = models.CharField(max_length=15,
        choices=CAPITALIZACAO, null=True, blank=True)
    # Identificador de conta da corretora IB
    ib_id = models.CharField(blank=True, null=True, max_length=15)
    # Identificador de conta da BTG
    btg_id = models.CharField(blank=True, null=True, max_length=15)
    # Identificador de conta XP
    xp_id = models.CharField(blank=True, null=True, max_length=15)
    # Identificador de conta Jefferies
    jefferies_id = models.CharField(blank=True, null=True, max_length=15)
    # Caixa padrão é o caixa em que o fundo recebe aportes. Quando há
    # movimentação de caixa sem caixa especificado, o caixa padrão é usado
    caixa_padrao = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    # Indica qual calendário o fundo segue.
    calendario = models.ForeignKey('calendario.Calendario', on_delete=models.PROTECT)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Fundos'

    def __str__(self):
        return '%s' % (self.nome)

    def fechar_fundo(self, data_referencia):
        """
        FECHAMENTO DE FUNDO
        Para fazer o fechamento de um fundo em uma determinada data de referência, é
        preciso:
            - Fechar todas as boletas do fundo que ainda não foram fechadas.
            - Reunir todos os vértices referentes ao fundo na data de referencia.
            - Verificar, no app Mercado, se há algum provento cuja ex-date seja na
        data de referência. Se houver o ativo na carteira, deve processar o provento
        de forma apropriada:
            - Dividendo/JSCP:
                - Cria uma movimentação no ativo na data_ex
                - Criar um CPR com data de início na data ex e data de pagamento
                igual à data de pagamento do provento.
                - Cria uma provisão com data de pagamento igual à data de pagamento
                do provento, e valor financeiro igual ao valor bruto por ação *
                quantidade de ações na data.
            - Bonificação em ações:
                - Cria uma quantidade do ativo na data de pagamento do provento
                igual a (valor bruto - 1) * quantidade na data ex do provento.
            - Direitos de subscrição:
                - Cria uma quantidade do ativo representante do direito de
                subscrição na data ex do provento.
                - No momento em que a subscrição for paga, cria a movimentação de
                entrada do ativo e boleta de provisão para a saída de caixa para
                pagamento.
            - Reunir todas as quantidades referentes ao fundo, com data igual ou
        anterior à data de referência. Quantidades são cumulativas. Consolidar
        e descartar aqueles que ficarem zerados (seria possível verificar
        através da comparação das quantidades que estava presentes no vértice do
        dia anterior.)
            - Reunir todas as movimentações referentes ao fundo, com data igual
        à data de referência. Movimentações são pontuais.
            - Reunir todas as boletas de CPR com data de início inferior à data de
        referência e data de pagamento superior à data de referência. Se boletas de
        CPR criarem movimentações e quantidades, não haverá necessidade de reunir
        as boletas, pois seus efeitos já seriam sentidos pelas quantidades e
        movimentações.
        """
        pass

    def fechar_boletas_do_fundo(self, data_referencia):
        """
        Reúne todas as boletas relevantes para a data de referência e faz seu
        fechamento.
        """
        pass

class Administradora(models.Model):
    """
    Descreve a instituição que faz a admnistração do fundo.
    """
    nome = models.CharField(max_length=30)
    contato = GenericRelation('Contato')

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Administradoras'
    def __str__(self):
        return '%s' % (self.nome)

class Gestora(models.Model):
    """
    Descreve a instituição que faz a gestão do fundo.
    """
    nome = models.CharField(max_length=30)
    contato = GenericRelation('Contato')
    # Indica qual gestora somos nós
    anima = models.BooleanField(default=False)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Gestoras'

    def __str__(self):
        return '%s' % (self.nome)

class Distribuidora(models.Model):
    """
    Descreve a instituição distribuidora do fundo.
    """
    nome = models.CharField(max_length=30)
    contato = GenericRelation('Contato')

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Distribuidora'

    def __str__(self):
        return '%s' % (self.nome)

class Corretora(models.Model):
    """
    Descreve uma corretora, e informações relevantes para se calcular a taxa
    de corretagem cobrada quando uma operação é realizada por meio da
    corretora.
    """
    # Nome da Corretora - XP, Bradesco, etc..
    nome = models.CharField(max_length=20, unique=True)
    # Taxa fixa que é sempre cobrada na operação
    taxa_fixa = models.DecimalField(null=True, default=0,
        max_digits=7, decimal_places=5)
    # Taxa mínima que é cobrada na operação. Caso a taxa total da operação
    # não ultrapasse a taxa mínima, a taxa mínima é cobrada, caso
    # contrário, a taxa total é cobrada.
    taxa_minima = models.DecimalField(null=True, default=0,
        max_digits=7, decimal_places=5)
    # Taxa, em percentual, cobrada pela corretora, que incide sobre o
    # valor total das ações operadas.
    taxa_corretagem = models.DecimalField(null=True, default=0,
        max_digits=9, decimal_places=7)
    # Taxa, em percentual, cobrada pela Bolsa, que incide sobre o
    # valor total das ações operadas.
    emolumentos = models.DecimalField(null=True, default=0,
        max_digits=9, decimal_places=7)
    # Taxa em dinheiro cobrada por ação negociada, por exemplo, Jefferies,
    # que cobra 1 centavo por ação negociada.
    corretagem_por_acao = models.DecimalField(null=True, default=0,
        max_digits=9, decimal_places=7)
    # Taxa repassada a distribuidores de fundos, no caso de trade de
    # ações, como não há distribuidora, o valor é devolvido ao fundo.
    rebate = models.DecimalField(null=True, default=0,
        max_digits=9, decimal_places=7)
    # Pontos de contato na corretora
    contato = GenericRelation('Contato')

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Corretoras'

    def __str__(self):
        return '%s' % (self.nome)

    def custo_total_acoes(self, financeiro, quantidade):
        """
        Retorna o total de taxas para um trade de ações
        """
        return self.calcular_rebate(financeiro, quantidade) + \
            self.calcular_corretagem(financeiro, quantidade) + \
            self.calcular_emolumentos(financeiro, quantidade) - \
            abs(self.corretagem_por_acao*quantidade)

    def calcular_corretagem(self, financeiro, quantidade):
        """
        Calcula a corretagem de um trade de ações.
        """
        corretagem = -decimal.Decimal(self.taxa_corretagem)/100*abs(financeiro) - abs(self.taxa_fixa)
        if self.taxa_minima != 0:
            if abs(corretagem) < abs(self.taxa_minima):
                corretagem = -abs(self.taxa_minima)
        return decimal.Decimal(corretagem).quantize(decimal.Decimal('1.00'))

    def calcular_emolumentos(self, financeiro):
        """
        Calcula os emolumentos de um trade de ações.
        """
        return -abs(financeiro)*abs(self.emolumentos)/100

    def calcular_rebate(self, financeiro, quantidade):
        """
        Calcula o rebate que é devolvido ao gestor.
        """
        return abs((1-self.rebate/100)*self.calcular_corretagem(financeiro, quantidade))

class Custodiante(models.Model):
    """
    Descreve quem é a custodiante do fundo/corretora.
    """
    nome = models.CharField(max_length=30)
    contato = GenericRelation('Contato')

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Custodiantes'
    def __str__(self):
        return '%s' % (self.nome)

class Contato(models.Model):
    """
    Modelo para armazenar pontos de contato nas instituições.
    """
    nome = models.CharField(max_length=30)
    telefone = PhoneNumberField()
    email = models.EmailField()
    area = models.CharField(max_length=50)
    observacao = models.TextField()

    limit = models.Q(app_label='fundo', model='administradora') | \
        models.Q(app_label='fundo', model='corretora') | \
        models.Q(app_label='fundo', model='distribuidora') | \
        models.Q(app_label='fundo', model='gestora')
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Contatos'

    def __str__(self):
        return '%s' % (self.nome)

class Carteira(BaseModel):
    """
    Descreve a carteira de um fundo ao final do dia numa determinada data.
    """
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    vertices = models.ManyToManyField('Vertice')
    data = models.DateField()
    cota = models.DecimalField(max_digits=15, decimal_places=6)

    class Meta:
        ordering = ['fundo']
        verbose_name_plural = 'Carteira'

class Vertice(BaseModel):
    """
    Um vertice descreve uma relacao entre carteira e ativo, indicando o quanto
    do ativo a carteira possui, e o quanto do ativo foi movimentado no dia.
    A quantidade e movimentação são salvos como valores ao invés de chave
    estrangeira para que a busca no banco de dados seja mais rápida. Uma
    outra tabela guarda a relação entre os modelos para que seja possível
    explodir um vértice entre várias quantidades/movimentações feitas.

    Criação de vértices em relação ao CPR:
        - CPR: Vértices de CPR possuem uma quantidade igual ao valor financeiro
    da boleta de CPR. Na data de pagamento, sua quantidade deve zerar. Deve
    haver uma movimentação de entrada e de saída do CPR, na data de início e na
    data de pagamento.
        - Empréstimo: Possui apenas quantidade. A movimentação ocorre no ativo
    e no caixa do fundo.
        - Acúmulo: Acúmulo são CPRs de despesas projetadas para serem cobradas
    no futuro. Não possuem movimentação de entrada, apenas de saída, quando a
    boleta é paga.
        - Diferimento: Quando uma despesa inesperada é paga, o diferimento serve
    para atenuar o efeito do pagamento da despesa ao longo do tempo. Possui uma
    movimentação de entrada.
    """
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    custodia = models.ForeignKey('Custodiante', on_delete=models.PROTECT)
    # Quantidade do ativo.
    quantidade = models.DecimalField(decimal_places=6, max_digits=20)
    # Valor financeiro do ativo.
    valor = models.DecimalField(decimal_places=2, max_digits=20)
    # Preço do ativo.
    preco = models.DecimalField(decimal_places=6, max_digits=20)
    movimentacao = models.DecimalField(decimal_places=6, max_digits=20, default=decimal.Decimal(0))
    data = models.DateField()

    # O content_type pode ser tanto um ativo quanto uma boleta de CPR
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='relacao_ativo')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['fundo']
        verbose_name_plural = 'Vértices'

class Quantidade(BaseModel):
    """
    Uma quantidade de um ativo ou CPR é gerada quando o ativo é operado.
    """
    # Quantidade do ativo.
    qtd = models.DecimalField(decimal_places=6, max_digits=20)
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    data = models.DateField()

    # Content type para servir de ForeignKey de qualquer boleta a ser
    # inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='quantidade_boleta')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # ContentType para servir de ForeignKey para ativo ou CPR
    tipo_quantidade = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='quantidade_ativo')
    tipo_id = models.PositiveIntegerField()
    objeto_quantidade = GenericForeignKey('tipo_quantidade', 'tipo_id')

    def __str__(self):
        return '%s' % (self.content_object.__str__())

class Movimentacao(BaseModel):
    """
    Uma movimentação representa a movimentação financeira de algo, ações,
    caixa, CPR, etc.
    """
    # Valor financeiro da movimentação
    valor = models.DecimalField(decimal_places=6, max_digits=20)
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    data = models.DateField()

    # Content type para servir de ForeignKey de qualquer boleta a ser
    # inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='movimentacao_boleta')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # ContentType para servir de ForeignKey para ativo ou CPR
    tipo_movimentacao = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='movimentacao_ativo')
    tipo_id = models.PositiveIntegerField()
    objeto_movimentacao = GenericForeignKey('tipo_movimentacao', 'tipo_id')

    def __str__(self):
        return '%s' % (self.content_object.__str__())

class CasamentoVerticeQuantidade(BaseModel):
    """
    Relaciona o ID dos Vértices e das Quantidades, para que seja possível
    explodir um vértice entre todas as quantidades/operações feitas.
    """
    vertice = models.ForeignKey('Vertice', on_delete=models.PROTECT)
    quantidade = models.ForeignKey('Quantidade', on_delete=models.PROTECT)

class CasamentoVerticeMovimentacao(BaseModel):
    """
    Relaciona o ID de Vértices e Movimentações, para que seja possível
    explodir um vértice entre todas as movimentações/operações feitas.
    """
    vertice = models.ForeignKey('Vertice', on_delete=models.PROTECT)
    movimentacao = models.ForeignKey('Movimentacao', on_delete=models.PROTECT)

class Cotista(BaseModel):
    """
    Armazena informações de cotistas dos fundos. Eles podem ser outros
    fundos ou pessoas.
    """
    # Nome do cotista
    nome = models.CharField(max_length=100, unique=True)
    # Número do documento de identificação - CPF/CNPJ
    n_doc = models.CharField(max_length=20, blank=True, null=True)
    # Cota média é o parâmetero para o cálculo do imposto de renda do cotista.
    # Ela é determinada pela média ponderada do valor da cota dos certificados
    # de passivo pela quantidade de cotas ainda aplicada.
    cota_media = models.DecimalField(max_digits=15, decimal_places=7, blank=True, null=True)
    # Se o cotista for um fundo gerido, preenche este campo
    fundo_cotista = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT,
        null=True, blank=True, unique=True)


class CertificadoPassivo(BaseModel):
    """
    A cada movimentação de passivo de fundo feita, um certificado passivo é
    criado para registrar quantas cotas, valor financeiro, IR calculado,
    é movimentado.
    """
    # Cotista que fez a movimentação de passivo.
    cotista = models.ForeignKey('fundo.Cotista', on_delete=models.PROTECT)
    # Quantidade de cotas que foram aplicadas originalmente.
    qtd_cotas = models.DecimalField(max_digits=15, decimal_places=7)
    # Valor da cota no momento da aplicação
    valor_cota = models.DecimalField(max_digits=10, decimal_places=2)
    # Quantidade de cotas desta série que ainda estão aplicadas.
    # Conforme o cotista realiza resgates do fundo, cotas de certificados mais
    # antigos são resgatadas, aumentando o valor da cota média.
    cotas_aplicadas = models.DecimalField(max_digits=15, decimal_places=7)
    # Data da aplicação
    data = models.DateField()

class CPR(models.Model):
    """
    Armazena informações sobre CPR do fundo.
    """
    nome = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=20, decimal_places=6)
    data = models.DateField()
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    vertice = GenericRelation('fundo.Vertice')

    # Chave estrangeira para a boleta originadora do CPR, caso aplicável.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='boleta', blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
