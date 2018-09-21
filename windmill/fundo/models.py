"""
Modelos deste app servem para armazenar informações e processar eventos de
fundos geridos.
Responsabilidades deste app:
    - Executar funções relacionadas ao fundo:
        - Fechamento diário para cálculo de cota.
        - Fechamento mensal para cálculo de cota.
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Fundo(models.Model):
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
    # mensalmente.
    capitalizacao_taxa_adm = models.CharField(max_length=15,
        choices=CAPITALIZACAO, null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Fundos'

    def __str__(self):
        return '%s' % (self.nome)

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

class Carteira(models.Model):
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

class Vertice(models.Model):
    """
    Um vertice descreve uma relacao entre carteira e ativo, indicando o quanto
    do ativo a carteira possui, e o quanto do ativo foi movimentado no dia.
    A quantidade e movimentação são salvos como valores para que a busca no
    banco de dados seja mais rápida. Uma outra tabela guarda a relação
    entre os modelos para que seja possível explodir um vértice entre várias
    quantidades/movimentações feitas.
    """
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    ativo = models.ForeignKey('ativos.Ativo', on_delete=models.PROTECT)
    custodia = models.ForeignKey('Custodiante', on_delete=models.PROTECT)
    quantidade = models.DecimalField(decimal_places=6, max_digits=20)
    valor = models.DecimalField(decimal_places=6, max_digits=20)
    preco = models.DecimalField(decimal_places=6, max_digits=20)
    movimentacao = models.DecimalField(decimal_places=6, max_digits=20)
    data = models.DateField()

    class Meta:
        ordering = ['fundo']
        verbose_name_plural = 'Vértices'

class Quantidade(models.Model):
    """
    Uma quantidade de um objeto é gerada quando o ativo é operado. O ID da
    operação indica quando a quantidade
    """
    # Quantidade do ativo.
    qtd = models.DecimalField(decimal_places=6, max_digits=20)
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    data = models.DateField()

    # Content type para servir de ForeignKey de qualquer boleta a ser
    # inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '%s' % (self.content_object.__str__())



class Movimentacao(models.Model):
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
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '%s' % (self.content_object.__str__())

class CasamentoVerticeQuantidade(models.Model):
    """
    Relaciona o ID dos Vértices e das Quantidades, para que seja possível
    explodir um vértice entre todas as quantidades/operações feitas.
    """
    vertice = models.ForeignKey('Vertice', on_delete=models.PROTECT)
    quantidade = models.ForeignKey('Quantidade', on_delete=models.PROTECT)

class CasamentoVerticeMovimentacao(models.Model):
    """
    Relaciona o ID de Vértices e Movimentações, para que seja possível
    explodir um vértice entre todas as movimentações/operações feitas.
    """
    vertice = models.ForeignKey('Vertice', on_delete=models.PROTECT)
    movimentacao = models.ForeignKey('Movimentacao', on_delete=models.PROTECT)

class Cotista(models.Model):
    """
    Armazena informações de cotistas dos fundos. Eles podem ser outros
    fundos ou pessoas.
    """

class CPR(models.Model):
    """
    Armazena informações sobre CPR do fundo.
    """
