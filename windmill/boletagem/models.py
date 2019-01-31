"""
Modelos deste app são voltados para a gravação de operações e inserção de
eventos no sistema.
Responsabilidades deste app:
    - Processamento de input de informações de mercado.
    - Repasse de informações aos apps responsáveis pelas informações
    processadas.

Funcionamento:
    - Boletas de ativos geram Movimentações e Quantidades dos seus respectivos
    ativos no app de Fundo. Movimentações e Quantidades são modelos do app
    "Fundo", e são consolidados em Vértices, que compõem uma Carteira.
    No fechamento de boletas de ativos, são geradas boletas de CPR e provisão,
    para refletir o CPR do ativo e a movimentação de caixa causada pela
    operação com o ativo.
    - Boletas de CPR geram CPRs, que, por sua vez, geram Movimentações e
    Quantidades de CPR.
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

Sobre o tratamento de boletas do ponto de vista de processo do sistema:
    - Ao serem boletados, as boletas devem ter seus campos "limpos" por métodos
    "clean_<field>()". Desta forma, validamos informações que o usuário insere
    no sistema.
    - As boletas podem ser fechadas. Isso significa que as informações
    relevantes foram todas inseridas, e todos os objetos relevantes relacionados
    foram criados, como Quantidade do ativo, e boletas de CPR e provisão.
    - Boletas em aberto (que ainda não criaram todos os objetos relacionados)
    são fechadas diariamente.
    - No fechamento da boleta:
        1 - Se verifica no sistema se há informações disponíveis para completar
        a boleta.
        2 - Os objetos relacionados à boleta são criados.
        O método 'fechado' verifica se foram criados todos os objetos.
    - Quando boletas são atualizadas com alguma informação, os objetos
    relacionados devem ser atualizados com as informações relevantes também.

"""
import datetime
from django.utils import timezone
import decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import ativos.models as am
import fundo.models as fm
import mercado.models as mm

# Create your models here.
# class BaseModelQuerySet(models.query.QuerySet):
#     def delete(self):
#         return super(BaseModelQuerySet, self).update(deletado_em=timezone.now())
#
#     def hard_delete(self):
#         return super(BaseModelQuerySet, self).delete()
#
#     def alive(self):
#         return self.filter(deletado_em=None)
#
#     def dead(self):
#         return self.exclude(deletado_em=None)
#
# class BaseModelManager(models.Manager):
#     def __init__(self, *args, **kwargs):
#         self.alive_only = kwargs.pop('alive_only', True)
#         super(BaseModelManager, self).__init__(*args, **kwargs)
#
#     def get_queryset(self):
#         if self.alive_only:
#             return BaseModelQuerySet(self.model).filter(deletado_em=None)
#         return BaseModelQuerySet(self.model)
#
#     def hard_delete(self):
#         return self.get_queryset().hard_delete()

class BaseModel(models.Model):
    """
    Classe base para criar campos comuns a todas as classes, como 'criado em'
    ou 'atualizado em'
    """
    deletado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # objects = BaseModelManager()
    # all_objects = BaseModelManager(alive_only=False)

    class Meta:
        abstract = True

    # def delete(self):
    #     self.deletado_em = timezone.now()
    #     self.save()
    #
    # def hard_delete(self):
    #     super(BaseModel, self).delete()



class BoletaAcao(BaseModel):
    """
    Representa a boleta de um trade de ações. A boleta de ações deve ter todas
    as informações necessárias para a geração das boletas e quantidades
    no momento em que ela é armazenada no sistema.
    O custo total de corretagem pode ser alterado posteriormente, para o pró
    ximo
    """
    OPERACAO = (
        ('C', 'C'),
        ('V', 'V')
    )

    acao = models.ForeignKey("ativos.Acao", on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today, null=False)
    data_liquidacao = models.DateField(null=False)
    corretora = models.ForeignKey("fundo.Corretora", null=False, on_delete=models.PROTECT)
    corretagem = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    custodia = models.ForeignKey('fundo.Custodiante', null=False, on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.IntegerField()
    preco = models.DecimalField(max_digits=13, decimal_places=7)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_acao')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_acao')

    class Meta:
        verbose_name_plural = "Boletas de operação de ações"

    def __str__(self):
        return "Operação de %s executada em %s." % (self.acao, self.data_operacao)

    def clean_data_liquidacao(self):
        """
        Data de liquidação da boleta deve ser maior que a data de operação.
        """
        if self.data_liquidacao < self.data_operacao:
            raise ValidationError(_('Insira uma data de liquidação maior que a data de operação.'))

    def clean_quantidade(self):
        """
        Alinha o valor de quantidade com a operação.
        """
        if self.operacao == 'V':
            self.quantidade = -abs(self.quantidade)
        else:
            self.quantidade = abs(self.quantidade)

    def clean_preco(self):
        """
        Não aceita preços negativos, apenas positivos. Converte o número do
        preço para um decimal com 6 casas decimais de detalhe.
        """
        self.preco = decimal.Decimal(self.preco).quantize(decimal.Decimal('1.000000'))
        if self.preco < 0 :
            self.preco = -self.preco

    def clean_corretagem(self):
        """
        Caso a corretagem não tenha sido inserida, calcula a corretagem
        """
        if self.corretagem == None:
            self.corretagem = self.corretora.calcular_corretagem(self.quantidade * self.preco, self.quantidade)

    def save(self, *args, **kwargs):
        """
        Caso o valor da corretagem não tenha sido inserido, calcula.
        """
        self.clean_data_liquidacao()
        self.clean_quantidade()
        self.clean_preco()
        self.clean_corretagem()
        super().save(*args, **kwargs)

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

    def fechado(self):
        """
        Determina se a boleta já foi fechada. Uma boleta é considerada fechada
        quando a movimentação e quantidade do ativo já tiverem sido gerados,
        assim como a boleta de CPR e provisão relacionadas.
        """
        return self.boleta_provisao.all().exists() and \
            self.boleta_CPR.all().exists() and \
            self.relacao_quantidade.all().exists() and \
            self.relacao_movimentacao.all().exists()

    def criar_boleta_provisao(self):
        """
        Cria uma boleta de provisão de acordo com os parâmetros da boleta
        de ação. Se já houver uma boleta de provisão criada, não há necessidade
        de criar outra.
        """
        # Checar se já há boleta de provisão criada relacionada com esta.
        if self.boleta_provisao.all().exists() == False:
            op = ''
            if self.operacao == "C":
                op = 'Compra '
            else:
                op = 'Venda '
            # Criar boleta de provisão
            boleta_provisao = BoletaProvisao(
                descricao = op + self.acao.nome,
                caixa_alvo = self.caixa_alvo,
                fundo = self.fundo,
                data_pagamento = self.data_liquidacao,
                # A movimentação de caixa tem sinal oposto à variação de quantidade
                financeiro = decimal.Decimal(-(self.preco * self.quantidade) + self.corretagem).quantize(decimal.Decimal('1.00')),
                content_object = self
            )
            boleta_provisao.full_clean()
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
                valor_cheio = decimal.Decimal(-(self.preco * self.quantidade) + self.corretagem).quantize(decimal.Decimal('1.00')),
                data_inicio = self.data_operacao,
                data_pagamento = self.data_liquidacao,
                fundo = self.fundo,
                content_object = self
            )
            boleta_CPR.full_clean()
            boleta_CPR.save()

    def criar_quantidade(self):
        """
        Cria uma quantidade do ativo de acordo com os parâmeteros da boleta
        de ação. Se já houver uma quantidade criada, não há necessidade
        de criar outra.
        """
        # Checar se há quantidade já criada
        from fundo.models import Quantidade, Movimentacao
        if self.relacao_quantidade.all().exists() == False:
            # Criar Quantidade do Ativo
            acao_quantidade = Quantidade(
                qtd = self.quantidade,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_quantidade = self.acao
            )
            acao_quantidade.full_clean()
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
            from fundo.models import Quantidade, Movimentacao
            valor = self.preco * self.quantidade + self.corretagem
            valor = decimal.Decimal(valor).quantize(decimal.Decimal('1.000000'))
            acao_movimentacao = Movimentacao(
                valor = valor,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_movimentacao = self.acao
            )
            acao_movimentacao.full_clean()
            acao_movimentacao.save()

class BoletaRendaFixaLocal(BaseModel):
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
    data_liquidacao = models.DateField(null=True, blank=True)
    corretora = models.ForeignKey('fundo.Corretora', null=False, on_delete=models.PROTECT)
    custodia = models.ForeignKey('fundo.Custodiante', on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco = models.DecimalField(max_digits=13, decimal_places=6)
    taxa = models.DecimalField(max_digits=10, decimal_places=6)
    corretagem = models.DecimalField(max_digits=13, decimal_places=6)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_rfloc')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_rfloc')

    class Meta:
        verbose_name_plural = "Boletas de operação de renda fixa local"

    def __str__(self):
        operacao = ''
        if self.operacao == 'C':
            operacao = 'Compra'
        else:
            operacao = 'Venda'
        return "%s de %s executada em %s." % (operacao, self.ativo, self.data_operacao)

    def save(self, *args, **kwargs):
        self.clean()
        if self.corretagem is None:
            self.corretagem = -abs(self.corretora.taxa_fixa)
        super().save(*args, **kwargs)

    def clean_data_liquidacao(self):
        if self.data_liquidacao < self.data_operacao:
            raise ValidationError(_('A data de liquidação não pode ser anterior à data de operação.'))

    def clean_quantidade(self):
        if self.operacao == 'C':
            self.quantidade = abs(self.quantidade)
        else:
            self.quantidade = -abs(self.quantidade)

    def clean_preco(self):
        self.preco = decimal.Decimal(self.preco).quantize(decimal.Decimal('1.000000'))
        if self.preco < 0:
            raise ValidationError(_("Preço inválido, informe um preço de valor positivo."))

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

    def fechado(self):
        """
        Determina se a boleta já foi fechada. Uma boleta é considerada fechada
        quando a movimentação e quantidade do ativo já tiverem sido gerados,
        assim como a boleta de CPR e provisão relacionadas.
        """
        return self.boleta_provisao.all().exists() and \
            self.boleta_CPR.all().exists() and \
            self.relacao_quantidade.all().exists() and \
            self.relacao_movimentacao.all().exists()

    def criar_boleta_provisao(self):
        """
        Cria uma boleta de provisão de acordo com os parâmeteros da boleta
        de ação. Se já houver uma boleta de provisão criada, não há necessidade
        de criar outra.
        """
        # Checar se já há boleta de provisão criada relacionada com esta.
        if self.boleta_provisao.all().exists() == False:
            op = ''
            if self.operacao == "C":
                op = 'Compra '
            else:
                op = 'Venda '
            # Criar boleta de provisão
            boleta_provisao = BoletaProvisao(
                descricao = op + self.ativo.nome,
                caixa_alvo = self.caixa_alvo,
                fundo = self.fundo,
                data_pagamento = self.data_liquidacao,
                # A movimentação de caixa tem sinal oposto à variação de quantidade
                financeiro = - (self.preco * self.quantidade) + self.corretagem,
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
                descricao = op + self.ativo.nome,
                valor_cheio = -(self.preco * self.quantidade),
                data_inicio = self.data_operacao,
                data_pagamento = self.data_liquidacao,
                fundo = self.fundo,
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
            from fundo.models import Quantidade, Movimentacao
            acao_quantidade = Quantidade(
                qtd = self.quantidade,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_quantidade = self.ativo
            )
            acao_quantidade.save()

    def criar_movimentacao(self):
        """
        Cria uma movimentação de acordo com os parâmeteros da boleta.
        Se já houver uma movimentação criada, não há necessidade de
        criar outra.
        """
        # Checar se há movimentação já criada
        if self.relacao_movimentacao.all().exists() == False:
            # Criar Movimentacao do Ativo
            from fundo.models import Quantidade, Movimentacao
            acao_movimentacao = Movimentacao(
                valor = round(self.preco * self.quantidade + self.corretagem, 2),
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_movimentacao = self.ativo
            )
            acao_movimentacao.save()

class BoletaRendaFixaOffshore(BaseModel):
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
    custodia = models.ForeignKey('fundo.Custodiante', on_delete=models.PROTECT)
    corretagem = models.DecimalField(max_digits=8, decimal_places=2)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nominal = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    taxa = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    # Relações genéricas que permitem ligar a boleta de renda fixa offshore à
    # boletas de provisão, CPR, quantidade e movimentação.
    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_rfoff')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_rfoff')

    def clean_data_liquidacao(self):
        """
        Valida a data de liquidação da boleta.
        """
        if self.data_liquidacao < self.data_operacao:
            raise ValidationError(_("Data de liquidação inválida. Insira uma data maior ou igual à data de operação."))

    def clean_quantidade(self):
        """
        Alinha a quantidade do ativo com a operação. Em operação de compra,
        a quantidade deve ser positiva. Em operação de venda, a quantidade
        deve ser negativa.
        """
        if self.operacao == "C":
            self.quantidade = abs(self.quantidade)
        elif self.operacao == "V":
            self.quantidade = -abs(self.quantidade)

    def clean_preco(self):
        """
        Verifica se o preço não é um valor negativo
        """
        self.preco = decimal.Decimal(self.preco).quantize(decimal.Decimal('1.000000'))
        if self.preco < 0:
            raise ValidationError(_("Preço inválido, insira um valor positivo para o preço."))

    def clean_taxa(self):
        """
        Converte o número do preço para um decimal com 6 casas decimais de
        detalhe.
        """
        self.taxa = decimal.Decimal(self.taxa).quantize(decimal.Decimal('1.000000'))

    def fechar_boleta(self):
        """
        Verifica as informações da boleta e gera quantidade, movimentação,
        boletas de CPR e provisão para a boleta.
        """
        self.criar_movimentacao()
        self.criar_quantidade()
        self.criar_boleta_CPR()
        self.criar_boleta_provisao()

    def fechado(self):
        return self.boleta_provisao.all().exists() and \
            self.boleta_CPR.all().exists() and \
            self.relacao_quantidade.all().exists() and \
            self.relacao_movimentacao.all().exists()

    def criar_movimentacao(self):
        """
        Cria uma movimentação do ativo relacionada a essa boleta, apenas se
        a boleta não possuir nenhuma movimentação ligada a ela
        """
        if self.relacao_movimentacao.all().exists() == False:
            from fundo.models import Quantidade, Movimentacao
            ativo_movimentacao = Movimentacao(
                valor = round(self.quantidade * self.preco + self.corretagem, 2),
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_movimentacao = self.ativo
            )
            ativo_movimentacao.clean()
            ativo_movimentacao.save()

    def criar_quantidade(self):
        """
        Uma quantidade do ativo é criada para movimentar a quantidade de ativos na carteira.
        """
        if self.relacao_quantidade.all().exists() == False:
            self.clean_quantidade()
            from fundo.models import Quantidade, Movimentacao
            ativo_quantidade = Quantidade(
                qtd = self.quantidade,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_quantidade = self.ativo
            )
            ativo_quantidade.clean()
            ativo_quantidade.save()

    def criar_boleta_CPR(self):
        """
        É criado um CPR para o trade.
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
                descricao = op + self.ativo.nome,
                valor_cheio = -(self.preco * self.quantidade) + self.corretagem,
                data_inicio = self.data_operacao,
                data_pagamento = self.data_liquidacao,
                fundo = self.fundo,
                content_object = self
            )
            boleta_CPR.save()

    def criar_boleta_provisao(self):
        """
        Cria uma boleta de provisão de acordo com os parâmeteros da boleta
        de ação. Se já houver uma boleta de provisão criada, não há necessidade
        de criar outra.
        """
        # Checar se já há boleta de provisão criada relacionada com esta.
        if self.boleta_provisao.all().exists() == False:
            op = ''
            i_op = 1
            if self.operacao == "C":
                op = 'Compra '
            else:
                op = 'Venda '
                i_op = -1
            # Criar boleta de provisão
            boleta_provisao = BoletaProvisao(
                descricao = op + self.ativo.nome,
                caixa_alvo = self.caixa_alvo,
                fundo = self.fundo,
                data_pagamento = self.data_liquidacao,
                # A movimentação de caixa tem sinal oposto à variação de quantidade
                financeiro = -(self.preco * abs(self.quantidade)*i_op) + self.corretagem,
                content_object = self

            )
            boleta_provisao.save()

class BoletaFundoLocal(BaseModel):
    """
    Representa uma operação de cotas de fundo local. Processado da mesma maneira
    que a boleta de ação.
    Ao salvar uma boleta:
        Todas as informações devem ser limpadas pelos métodos "clean_<campo>()"
    Ao fazer o fechamento de uma boleta:
        A boleta deve ser atualizada com informações do sistema, se estiverem
    disponíveis.
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
    financeiro = models.DecimalField(max_digits=16, decimal_places=6, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    preco = models.DecimalField(max_digits=17, decimal_places=8, blank=True, null=True)
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)
    custodia = models.ForeignKey('fundo.Custodiante', on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_fundo_local')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_fundo_local')
    relacao_passivo = GenericRelation('BoletaPassivo', related_query_name='mov_origem')

    def save(self, *args, **kwargs):
        self.clean_financeiro()
        # self.clean_data_cotizacao()
        # self.clean_data_liquidacao()
        # self.clean_quantidade()
        super().save(*args, **kwargs)

    def clean_financeiro(self):
        """
        Valida o campo financeiro. Caso quantidade e preço estejam preenchidos,
        financeiro deve ser calculado como sendo igual a preço * quantidade.
        Caso algum dos dois não esteja preenchido, financeiro deve estar.
        """
        if self.quantidade == None or self.preco == None:
            if self.financeiro == None and self.operacao != "Resgate Total":
                raise ValidationError(_("Informe o financeiro ou quantidade e preço."))
        elif self.quantidade != None and self.preco != None and self.financeiro == None:
            self.financeiro = self.quantidade * self.preco

    def clean_data_liquidacao(self):
        """
        Data de liquidação deve ser menor que data de operação.
        """
        if self.data_liquidacao < self.data_operacao:
            raise ValidationError(_("Insira uma data de liquidação válida. Ela deve ser menor que data de operação."))

    def clean_data_cotizacao(self):
        """
        Data de cotização deve ser menor que a data de operação. A data de cotização
        deve ser menor ou igual à data de liquidação no caso de resgates.
        """
        if self.data_cotizacao < self.data_operacao:
            raise ValidationError(_('Insira uma data de cotização válida. Ela deve ser menor que a data de operação.'))
        if self.data_liquidacao < self.data_cotizacao and "Resgate" in self.operacao:
            raise ValidationError(_('Insira uma data de cotização válida. Em caso de resgate, ela deve ser menor ou igual que a data de liquidação.'))

    def clean_quantidade(self):
        """
        Alinha o sinal da quantidade com a operação. Caso seja uma operação
        de aplicação, a quantidade deve ser positiva. Caso seja um resgate,
        a quantidade deve ser negativa.
        Caso a quantidade seja
        """
        if self.quantidade == None:
            if self.cota_disponivel() == True or self.preco != None:
                if self.operacao == "Aplicação":
                    self.quantidade = abs(self.financeiro)/self.preco
                elif self.operacao == "Resgate":
                    self.quantidade = -abs(self.financeiro)/self.preco
                elif self.operacao == "Resgate Total":
                    # TODO: Em caso de resgate total, a quantidade é igual à posição inteira do ativo na carteira.
                    pass
        if self.operacao == "Aplicação" and self.quantidade is not None:
            self.quantidade = abs(self.quantidade)
            self.clean_financeiro()
        elif "Resgate" in self.operacao and self.quantidade is not None:
            self.quantidade = -abs(self.quantidade)
            self.clean_financeiro()

    def fechado(self):
        """
        Retorna True se houver boleta de provisão e CPR associadas a essa boleta,
        assim como quantidade e movimento do ativo.
        """
        passivo_fechado = True
        if self.passivo() == True:
            if self.relacao_passivo.all().exists() == False:
                passivo_fechado = False

        return self.boleta_provisao.all().exists() and \
            self.boleta_CPR.all().exists() and \
            self.relacao_quantidade.all().exists() and \
            self.relacao_movimentacao.all().exists() and passivo_fechado

    def passivo(self):
        """
        Retorna True se o ativo movimentado é um fundo gerido. Caso contrário,
        retorna False. Isto significa que há uma movimentação de passivo no
        fundo sofrendo a movimentação.
        """
        return self.ativo.gerido()

    def checa_fundo_passivo(self, fundo):
        """ fundo.Fundo -> Boolean
        Recebe um fundo, e checa com o ativo para ver se o fundo é o ativo sendo
        movimentado
        """
        return self.ativo.gestao == fundo

    def cota_disponivel(self):
        """
        Verifica se o valor da cota está disponível. Se estiver, atualiza a boleta
        com ele.
        """
        if self.preco == None:
            preco = mm.Preco.objects.filter(ativo=self.ativo, data_referencia=self.data_cotizacao).first()
            if preco == None:
                return False
            self.preco = decimal.Decimal(preco.preco_fechamento).quantize(decimal.Decimal('1.000000'))
            self.save()
            return True
        else:
            return True

    def fechar_boleta(self):
        """
        Faz o fechamento da boleta, de acordo com as informações disponíveis.
        Podemos criar as boletas de provisão e CPR independente de haver
        informação de cota da movimentação. Caso o ativo movimentado seja um
        fundo gerido, podemos gerar uma boleta de passivo. Quando a informação
        de cota estiver disponível, podemos criar a quantidade e movimentação
        do ativo.
        """
        self.atualizar_boleta()
        self.criar_boleta_provisao()
        self.criar_boleta_CPR()
        if self.quantidade is not None:
            self.criar_quantidade()
            self.criar_movimentacao()
        if self.passivo() == True:
            self.criar_boleta_passivo()

    def atualizar_boleta(self):
        """
        Busca informações no sistema para completar a boleta.
        """
        if self.preco == None:
            if self.cota_disponivel() == True:
                if self.quantidade is None and self.financeiro is not None:
                    self.quantidade = self.financeiro/self.preco
                    # Caso o ativo negociado seja um fundo gerido, atualiza a
                    # boleta de passivo gerada. Deve haver apenas uma boleta,
                    # logo, basta pegar a primeira da relacao_passivo
                    if self.passivo() == True and self.relacao_passivo.exists():
                        passivo = self.relacao_passivo.first()
                        passivo.cota = self.preco
                        passivo.save()
            self.clean_quantidade()
        if self.quantidade == None and self.preco != None:
            self.clean_quantidade()

    def criar_movimentacao(self):
        """
        Cria uma movimentação do ativo movimentado.
        """
        if self.relacao_movimentacao.all().exists() == False:
            self.clean_financeiro()
            from fundo.models import Quantidade, Movimentacao
            mov = Movimentacao(
                valor=self.financeiro,
                fundo=self.fundo,
                data=self.data_cotizacao,
                content_object=self,
                object_id=self.id,
                objeto_movimentacao=self.ativo,
                tipo_id=self.ativo.id
            )
            mov.full_clean()
            mov.save()

    def criar_quantidade(self):
        """
        Cria a quantidade do ativo movimentado, caso a boleta já não tenha
        criado.
        """
        # TODO: VERIFICAR SE O PREÇO DO ATIVO JÁ FOI INFORMADO PARA CRIAR
        # A MOVIMENTAÇÃO.
        if self.relacao_quantidade.all().exists() == False:
            self.clean_quantidade()
            from fundo.models import Quantidade, Movimentacao
            qtd = Quantidade(
                qtd=self.quantidade,
                fundo=self.fundo,
                data=self.data_cotizacao,
                content_object=self,
                objeto_quantidade=self.ativo
            )
            qtd.full_clean()
            qtd.save()

    def criar_boleta_CPR(self):
        """
        Cria a boleta de CPR da operação, caso já não tenha sido criada.
        """
        if self.boleta_CPR.all().exists() == False:
            # Clean na data de cotização para verificar se está tudo certo.
            self.full_clean()
            financeiro = 0
            if self.operacao == self.OPERACAO[0][0]:
                financeiro = -abs(self.financeiro)
            else:
                financeiro = abs(self.financeiro)
            if self.data_cotizacao < self.data_liquidacao:
                cpr = BoletaCPR(
                    descricao = self.operacao + " " + self.ativo.nome,
                    valor_cheio = financeiro,
                    data_inicio = self.data_cotizacao,
                    data_pagamento = self.data_liquidacao,
                    fundo = self.fundo,
                    content_object = self
                )
                cpr.save()
            else:
                cpr = BoletaCPR(
                    descricao = self.operacao + " " + self.ativo.nome,
                    valor_cheio = financeiro,
                    data_inicio = self.data_liquidacao,
                    data_pagamento = self.data_cotizacao,
                    fundo = self.fundo,
                    content_object = self
                )
                cpr.save()

    def criar_boleta_provisao(self):
        if self.boleta_provisao.all().exists() == False:
            provisao = BoletaProvisao(
                descricao=self.operacao + " " + self.ativo.nome,
                caixa_alvo=self.caixa_alvo,
                fundo=self.fundo,
                data_pagamento=self.data_liquidacao,
                # O valor financeiro movimentado é oposto do valor do ativo.
                # Se for uma aplicação, precisamos desembolsar dinheiro,
                # se for um resgate, recebemos dinheiro.
                financeiro= -self.financeiro.quantize(decimal.Decimal('1.00')),
                content_object=self
            )
            provisao.full_clean()
            provisao.save()

    def criar_boleta_passivo(self):
        """
        Quando o ativo movimentado é um fundo gerido, deve haver a geração
        de uma boleta de passivo para o fundo.
        """
        if self.relacao_passivo.all().exists() == False:
            # Busca cotista equivalente ao fundo
            cotista = fm.Cotista.objects.filter(fundo_cotista=self.fundo).first()
            if cotista is None:
                # Se for o primeiro aporte do fundo, cria o cotista equivalente.
                cotista = fm.Cotista(nome=self.fundo.nome,
                    fundo_cotista=self.fundo)
                cotista.save()
            passivo = BoletaPassivo(
                cotista=cotista,
                valor=self.financeiro.quantize(decimal.Decimal('1.00')),
                data_operacao=self.data_operacao,
                data_cotizacao=self.data_cotizacao,
                data_liquidacao=self.data_liquidacao,
                operacao=self.operacao,
                fundo=self.ativo.gestao,
                cota=self.preco,
                content_object=self
            )
            passivo.full_clean()
            passivo.save()

class BoletaFundoOffshore(BaseModel):
    """
    Representa uma operação de cotas de fundo offshore. Processado de acordo
    com o seu estado atual.
    A cada fechamento de dia, verifica se o preço para a cotização do ativo
    está disponível. Caso esteja disponível, cria a movimentação e quantidade
    do ativo.
    Quantidade e movimentação devem ser gerados quando as informações de
    cotização estão disponíveis, para que seja possível casar a variação
    de quantidade com a movimentação.
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

    OPERACAO = (
        ('Aplicação', 'Aplicação'),
        ('Resgate', 'Resgate'),
        ('Resgate Total', 'Resgate Total')
    )

    ativo = models.ForeignKey('ativos.Fundo_Offshore', on_delete=models.PROTECT)
    estado = models.CharField(max_length=80, choices=ESTADO)
    data_operacao = models.DateField(default=datetime.date.today)
    data_cotizacao = models.DateField()
    data_liquidacao = models.DateField()
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    financeiro = models.DecimalField(max_digits=16, decimal_places=6, blank=True, null=True)
    preco = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    operacao = models.CharField(max_length=13, choices=OPERACAO)
    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    custodia = models.ForeignKey('fundo.Custodiante', on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_fundo_off')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_fundo_off')
    boleta_passivo = GenericRelation('BoletaPassivo', related_query_name='passivo')

    def clean_preco(self):
        """
        Busca o valor do preco no banco de dados e preenche a boleta, caso esteja
        disponível.
        """
        if self.cotizavel() and self.preco == None:
            self.preco = mm.Preco.objects.filter(ativo=self.ativo, data_referencia=self.data_cotizacao).first().preco_fechamento
        elif self.preco != None:
            pass
        else:
            raise ValueError(_("Valor de cotização indisponível."))

    def clean_quantidade(self):
        """
        Valida o campo quantidade. Alinha o valor do campo com a operação
        realizada
        """
        if self.quantidade != None:
            if "Resgate" in self.operacao:
                self.quantidade = -abs(self.quantidade)
            else:
                self.quantidade = abs(self.quantidade)
        else:
            if "Resgate" in self.operacao:
                self.quantidade = -abs(self.financeiro)/self.preco
            else:
                self.quantidade = abs(self.financeiro)/self.preco

    def clean_financeiro(self):
        """
        Preenche o campo financeiro, se ele já não estiver preenchido. Deve
        haver um valor de cota e quantidade de cotas para que seja possível
        calculá-lo.
        """
        if self.financeiro == None:
            self.financeiro = self.preco * self.quantidade

    def fechado(self):
        """
        Determina se a boleta já foi fechada ou não.
        """
        if self.estado == "Concluído":
            return True
        else:
            return False

    def atualizar(self):
        """
        Verifica no sistem se há informações de valor de cota parar atualizar.
        Se houver, atualiza o preço da boleta e quantidade de cotas.
        """
        if self.cotizavel() == True:
            mm.Preco.objects.filter(ativo=self.ativo, data_referencia=self.data_cotizacao)
            self.preco = mm.Preco.objects.get(ativo=self.ativo, data_referencia=self.data_cotizacao).preco_fechamento
            self.quantidade = (self.financeiro/self.preco).quantize(decimal.Decimal('1.000000'))

    def cotizavel(self):
        """
        Determina se é possível cotizar a boleta, calculando a quantidade de
        cotas que serão movimentadas na operação.
        """
        if mm.Preco.objects.filter(ativo=self.ativo, data_referencia=self.data_cotizacao).exists() or self.preco != None:
            return True
        return False

    def passivo(self):
        """
        Determina se a boleta opera um ativo que é de nossa gestão, gerando uma
        boleta de passivo para o fundo sendo operado.
        """
        return self.ativo.gerido()

    def checa_fundo_passivo(self, fundo):
        """ fundo.Fundo -> Boolean
        Recebe um fundo, e checa com o ativo para ver se o fundo é o ativo sendo
        movimentado
        """
        return self.ativo.gestao == fundo and self.ativo.gestao.gestora.anima

    def fechar_boleta(self, data_referencia):
        """ datetime -> None
        CRIAÇÃO DE BOLETAS BASEADA NA TRANSIÇÃO DE ESTADOS:
            5.1.1 Boletagem de Operação no Manual Windmill:
            As transições ocorrem ao fechar a boleta, de acordo com as informações
        disponíveis no sistema. Ao executar o fechamento, devemos verificar no
        sistema quais informações estão disponíveis para que possamos executar a
        transição de estados de forma correta.
            Transição 1 - Pendente de cotização e liquidação -> pendente de cotização.
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
            Transição 2 - Pendente de cotização e liquidação -> pendente de liquidação.
                (Data de cotização anterior à data de liquidação)
                Condições necessárias:
                    - Valor financeiro a liquidar, quantidade de cotas e valor das cotas.
                    - Fechamento na data de cotização.
                Tarefas a executar:
                    - Cria a boleta de provisão, para saída de caixa.
                    - Cria a boleta de CPR de liquidação, com valor financeiro inverso
                    à boleta de operação.
                    - Cria a quantidade e movimentação do ativo.
                    - Atualizar estado.
            Transição 3 - Pendente de cotização -> Concluído
                Condições necessárias:
                    - Valor de cota disponível na data de cotização.
                    - Fechamento na data de cotização.
                Tarefas a executar:
                    - Atualiza a boleta de CPR de cotização com a data de pagamento igual
                à data de cotização.
                    - Cria a movimentação e a quantidade do ativo.
                    - Atualizar estado.
            Transição 4 - Pendente de liquidação -> Concluído.
                Condições necessárias:
                    - Liquidação da boleta de provisão
                    - Fechamento na data de liquidação.
                Tarefas a executar:
                    - Atualizar estado.
            Transição 5 - Pendente de cotização -> Pendente de informação de cotização
                Condições necessárias:
                    - Valor da cota indisponível no dia de cotização.
                    - Fechamento na data de cotização.
                Tarefas a executar:
                    - Atualizar estado.
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
            Transição 7 - Pendente de cotização e liquidação -> pendente de liquidação e informação de cotização.
                Condições necessárias:
                    - Informação da cota indisponível na data de cotização
                    - Fechamento na data de cotização.
                Tarefas a executar:
                    - Criação de uma boleta de CPR de cotização sem data de pagamento
                    definida e data de início igual à data de cotização.
                    - Criação de uma boleta de CPR de liquidação, com valor financeiro
                    contrário à boleta de cotização, data inicial igual à data de
                    cotização, e data de pagamento igual à data de liquidação.
                    - Criação de uma provisão.
                    - Atualizar estado.
            Transição 8 - Pendente de liquidação e informação de cotização -> concluído.
                Condições necessárias:
                    - Fechamento na data de liquidação;
                    - Cota disponível na data de liquidação.
                Tarefas a executar:
                    - Atualização da data de pagamento da boleta de CPR com a data
                    de inserção do valor da cota no sistema.
                    - Criação da movimentação e quantidade do ativo.
                    - Atualzar estado.
            Transição 9 - Pendente de liquidação e informação de cotização -> Pendente de informação de cotização.
                Condições necessárias:
                    - Fechamento na data de liquidação
                    - Cota indisponível na data de liquidação.
                Tarefas a executar:
                    - Apenas atualiza o estado.
        """
        print(self.estado)
        if self.estado != self.ESTADO[5][0]:
            if self.estado == self.ESTADO[4][0]: # Pendente de liquidação e cotização.
                if self.financeiro != None and data_referencia == self.data_liquidacao:
                    """
                    Transição 1 - Pendente de liquidação e cotização -> Pendente de cotização
                    """
                    self.criar_boleta_CPR_cotizacao()
                    self.criar_provisao()
                    self.estado = self.ESTADO[0][0]
                    self.save()
                    self.fechar_boleta(data_referencia)

                elif self.financeiro != None and (self.preco != None or self.cotizavel()) and \
                    data_referencia == self.data_cotizacao:
                    """
                    Transição 2 - Pendente de liquidação e cotização -> Pendente de liquidação.
                    """
                    """
                    CPR deve ser negativo quando a operação for de aplicação, e positivo
                    quando for de resgate
                    """
                    if self.preco == None:
                        self.clean_preco()
                        self.clean_quantidade()
                    if self.quantidade == None:
                        if self.operacao == self.OPERACAO[0][0]:
                            self.quantidade = abs((self.financeiro/self.preco).quantize(decimal.Decimal('1.000000')))
                        else:
                            self.quantidade = -abs((self.financeiro/self.preco).quantize(decimal.Decimal('1.000000')))
                    self.criar_boleta_CPR_liquidacao()
                    self.criar_provisao()
                    self.criar_movimentacao()
                    self.criar_quantidade()
                    if self.passivo():
                        self.criar_boleta_passivo()
                    self.estado = self.ESTADO[1][0]
                    self.save()
                    self.fechar_boleta(data_referencia)

                elif self.financeiro != None and self.cotizavel() == False and \
                    data_referencia == self.data_cotizacao and self.preco == None:

                    """
                    Transição 7 - Pendente de cotização e liquidação -> pendente de liquidação e informação de cotização.
                    """
                    self.criar_boleta_CPR_cotizacao()
                    self.criar_boleta_CPR_liquidacao()
                    self.criar_provisao()
                    self.estado = self.ESTADO[3][0]
                    if self.passivo():
                        self.criar_boleta_passivo()
                    self.save()

            elif self.estado == self.ESTADO[0][0] and (self.cotizavel() == True or self.preco != None)\
                and data_referencia == self.data_cotizacao:
                """
                Transição 3 - Pendente de cotização -> Concluído
                """
                financeiro = 0
                if self.operacao == self.OPERACAO[0][0]:
                    financeiro = decimal.Decimal(-abs(self.financeiro)).quantize(decimal.Decimal('1.00'))
                else:
                    financeiro = decimal.Decimal(abs(self.financeiro)).quantize(decimal.Decimal('1.00'))

                boleta = self.boleta_CPR.filter(valor_cheio=self.financeiro).first()
                boleta.data_pagamento = data_referencia
                boleta.save()
                self.clean_preco()
                self.clean_quantidade()
                self.criar_movimentacao(data_referencia)
                self.criar_quantidade(data_referencia)
                if self.passivo():
                    self.criar_boleta_passivo()
                self.save()

            elif self.estado == self.ESTADO[1][0] and data_referencia == self.data_liquidacao:
                """
                Transição 4 - Pendente de liquidação -> Concluído
                """
                self.estado = self.ESTADO[5][0]
                self.save()

            elif self.estado == self.ESTADO[0][0] and data_referencia == self.data_cotizacao and \
                self.cotizavel() == False:
                """
                Transição 5 - Pendente de cotização -> Pendente de informação de cotização
                """
                self.estado = self.ESTADO[2][0]
                if self.passivo():
                    self.criar_boleta_passivo()
                self.save()

            elif self.estado == self.ESTADO[2][0] and self.cotizavel() == True and \
                data_referencia > self.data_cotizacao:
                """
                Transição 6 - Pendente de informação de cotização -> Concluído
                """
                # Pegando boleta de cotização
                boleta = self.boleta_CPR.filter(valor_cheio=self.financeiro).first()
                boleta.data_pagamento = data_referencia
                boleta.save()
                self.clean_preco()
                self.clean_quantidade()
                self.criar_movimentacao(data_referencia)
                self.criar_quantidade(data_referencia)
                self.estado = self.ESTADO[5][0]
                if self.passivo():
                    # Atualiza a boleta de passivo com o valor da cota.
                    passivo = self.boleta_passivo.all().get(object_id=self.id)
                    if passivo.cota == None:
                        passivo.cota = self.preco
                        passivo.save()
                self.save()

            elif self.estado == self.ESTADO[3][0] and \
                (self.cotizavel() == True or self.preco != None) and \
                data_referencia == self.data_liquidacao:
                """
                Transição 8 - Pendente de liquidação e informação de cotização -> concluído
                """
                # Pegando boleta de CPR de cotização
                boleta = self.boleta_CPR.filter(valor_cheio=self.financeiro).first()
                boleta.data_pagamento = data_referencia
                self.clean_preco()
                self.clean_quantidade()
                self.criar_movimentacao(data_referencia)
                self.criar_quantidade(data_referencia)
                self.estado = self.ESTADO[5][0]
                if self.passivo():
                    passivo = self.boleta_passivo.all().get(object_id=self.id)
                    if passivo.cota == None:
                        passivo.cota = self.preco
                        passivo.save()
                boleta.save()
            elif self.estado == self.ESTADO[3][0] and self.cotizavel() == False and\
                self.preco == None and data_referencia == self.data_liquidacao:
                """
                Transição 9 - Pendente de liquidação e informação de cotização -> Pendente de informação de cotização.
                """
                self.estado = self.ESTADO[2][0]
                self.save()

    def criar_movimentacao(self, data_referencia=None):
        """
        Cria a movimentação do ativo. Deve ser criada no mesmo dia em que
        a quantidade do ativo é gerada, para que não haja descasamento da
        variação de quantidade e, no cálculo do retorno do ativo, não haja
        um retorno errado devido a esse descasamento
        """
        if self.relacao_movimentacao.all().exists() == False:
            if data_referencia == None:
                data_referencia = self.data_cotizacao
            self.clean_financeiro()
            from fundo.models import Quantidade, Movimentacao
            mov = Movimentacao(
                valor=self.financeiro,
                fundo=self.fundo,
                data=data_referencia,
                content_object=self,
                objeto_movimentacao=self.ativo
            )
            mov.full_clean()
            mov.save()

    def criar_quantidade(self, data_referencia=None):
        """
        Cria a variação de quantidade do ativo sendo negociado.
        """
        if self.relacao_quantidade.all().exists() == False:
            if data_referencia == None:
                data_referencia = self.data_cotizacao
            self.clean_quantidade()
            from fundo.models import Quantidade, Movimentacao
            qtd = Quantidade(
                qtd=self.quantidade.quantize(decimal.Decimal('1.000000')),
                fundo=self.fundo,
                data=data_referencia,
                content_object=self,
                objeto_quantidade=self.ativo
            )
            qtd.full_clean()
            qtd.save()

    def criar_boleta_CPR_cotizacao(self, data_referencia=None):
        """
        Cria uma boleta de cotização com as informações da boleta.
        """
        if self.boleta_CPR.all().filter(valor_cheio=self.financeiro).exists() == False:
            # Verifica se há preço. Se não houver, cria uma boleta de CPR sem
            # data de pagamento
            financeiro = 0
            if self.operacao == self.OPERACAO[0][0]:
                financeiro = decimal.Decimal(abs(self.financeiro)).quantize(decimal.Decimal('1.00'))
            else:
                financeiro = decimal.Decimal(-abs(self.financeiro)).quantize(decimal.Decimal('1.00'))
            if self.preco == None:
                if self.data_liquidacao < self.data_cotizacao:
                    cpr = BoletaCPR(
                        descricao="Cotização de " + self.ativo.nome,
                        valor_cheio=financeiro,
                        data_pagamento=data_referencia,
                        data_inicio=self.data_liquidacao,
                        fundo=self.fundo,
                        content_object=self
                    )
                    cpr.full_clean()
                    cpr.save()
                else:
                    cpr = BoletaCPR(
                        descricao="Cotização de " + self.ativo.nome,
                        valor_cheio=financeiro,
                        data_pagamento=data_referencia,
                        data_inicio=self.data_cotizacao,
                        fundo=self.fundo,
                        content_object=self
                    )
                    cpr.full_clean()
                    cpr.save()
            else:
                if self.data_liquidacao < self.data_cotizacao:
                    cpr = BoletaCPR(
                        descricao="Cotização de " + self.ativo.nome,
                        valor_cheio=financeiro,
                        data_pagamento=data_referencia,
                        data_inicio=self.data_liquidacao,
                        fundo=self.fundo,
                        content_object=self
                    )
                    cpr.full_clean()
                    cpr.save()
                else:
                    cpr = BoletaCPR(
                        descricao="Cotização de " + self.ativo.nome,
                        valor_cheio=financeiro,
                        data_pagamento=data_referencia,
                        data_inicio=self.data_cotizacao,
                        fundo=self.fundo,
                        content_object=self
                    )
                    cpr.full_clean()
                    cpr.save()

    def criar_boleta_CPR_liquidacao(self, data_referencia=None):
        """
        Cria uma boleta relacionada à liquidação da movimentação.
        Ela deve ter um valor contrário ao valor financeiro da boleta de
        CPR de cotização.
        """
        if self.boleta_CPR.all().filter(valor_cheio=-self.financeiro).exists() == False:
            financeiro = 0
            if self.operacao == self.OPERACAO[0][0]:
                financeiro = decimal.Decimal(-abs(self.financeiro)).quantize(decimal.Decimal('1.00'))
            else:
                financeiro = decimal.Decimal(abs(self.financeiro)).quantize(decimal.Decimal('1.00'))
            cpr = BoletaCPR(
                descricao="Liquidação de " + self.ativo.nome,
                valor_cheio=financeiro,
                data_pagamento=self.data_liquidacao,
                data_inicio=self.data_cotizacao,
                fundo=self.fundo,
                content_object=self
            )
            cpr.full_clean()
            cpr.save()

    def criar_provisao(self):
        """
        Cria provisão com base na data de liquidação da operação.
        """
        if self.boleta_provisao.all().exists() == False:
            provisao = BoletaProvisao(
                descricao=self.operacao + " de " + self.ativo.nome,
                caixa_alvo=self.caixa_alvo,
                fundo=self.fundo,
                data_pagamento=self.data_liquidacao,
                financeiro=-self.financeiro.quantize(decimal.Decimal('1.00')),
                content_object=self
            )
            provisao.full_clean()
            provisao.save()

    def criar_boleta_passivo(self):
        """
        Cria boleta de passivo, caso o ativo negociado seja um fundo gerido.
        """
        if self.boleta_passivo.all().exists() == False:
            cotista = fm.Cotista.objects.filter(fundo_cotista=self.fundo).first()
            if cotista == None:
                cotista = fm.Cotista(
                    nome=self.fundo.nome,
                    fundo_cotista=self.fundo
                )
                cotista.save()

            passivo = BoletaPassivo(
                cotista = cotista,
                valor=self.financeiro.quantize(decimal.Decimal('1.00')),
                data_operacao=self.data_operacao,
                data_cotizacao=self.data_cotizacao,
                data_liquidacao=self.data_liquidacao,
                operacao=self.operacao,
                fundo=self.ativo.gestao,
                cota=self.preco,
                content_object=self
            )
            passivo.full_clean()
            passivo.save()

class BoletaEmprestimo(BaseModel):
    """
    Representa uma operação de empréstimo de ações locais.
    CPR: Ao fazer o fechamento de uma boleta de empréstimo, caso não haja boleta
    de CPR, cria a boleta de CPR, com data de pagamento igual à data de vencimento.
    A cada dia, a boleta de CPR é atualizada com o novo valor financeiro do
    contrato. Caso o contrato seja liquidado antecipadamente, a boleta de CPR
    também deve ser atualizada. A atualização ocorre no fechamento da boleta.

    No momento, depende de um agente externo liquidando manualmente as boletas
    para funcionar corretamente.
    """
    # TODO: PARTE DE CPR.
    OPERACAO = (
        ('Doador', 'Doador'),
        ('Tomador', 'Tomador')
    )

    ativo = models.ForeignKey('ativos.Acao', on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    corretora = models.ForeignKey('fundo.Corretora', on_delete=models.PROTECT)
    custodia = models.ForeignKey('fundo.Custodiante', on_delete=models.PROTECT)
    data_vencimento = models.DateField()
    data_liquidacao = models.DateField(null=True, blank=True)
    reversivel = models.BooleanField()
    data_reversao = models.DateField(null=True, blank=True)
    operacao = models.CharField('Operação', max_length=10, choices=OPERACAO)
    comissao = models.DecimalField(max_digits=9, decimal_places=6)
    quantidade = models.DecimalField(max_digits=15, decimal_places=6)
    taxa = models.DecimalField(max_digits=8, decimal_places=6)
    preco = models.DecimalField(max_digits=10, decimal_places=6)
    boleta_original = models.ForeignKey('BoletaEmprestimo', on_delete=models.PROTECT, null=True, blank=True)
    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    calendario = models.ForeignKey('calendario.Calendario',
        on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_emprestimo')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_emprestimo')

    class Meta:
        verbose_name_plural = "Boletas de Empréstimo"

    def __str__(self):
        return "Empréstimo " + self.ativo.nome + " - " + self.operacao

    def save(self, *args, **kwargs):
        """
        Ao salvar uma boleta, caso não haja referencia para uma boleta original,
        a boleta salva é a boleta original, então o campo deve se referenciar
        a ele mesmo.
        """
        if self.boleta_original == None:
            super().save(*args, **kwargs)
            self.boleta_original = self
            super().save()
        else:
            super().save(*args, **kwargs)

    def clean_data_vencimento(self):
        """
        Faz validação do campo data_vencimento
        """
        if self.data_vencimento < self.data_operacao:
            raise ValidationError(_('A data de vencimento deve ser posterior à data de operação.'))
        if self.data_vencimento < self.data_reversao and self.data_reversao is not None:
            raise ValidationError(_('A data de vencimento deve ser superior à data de reversão.'))

    def clean_data_liquidacao(self):
        """
        Validação do campo data_liquidacao
        """
        if self.data_liquidacao <= self.data_operacao:
            raise ValidationError(_('A data de liquidação deve ser posterior à data de operação, anterior ou igual à data de vencimento e igual ou posterior à data de reversão.'))
        if self.data_liquidacao > self.data_vencimento:
            raise ValidationError(_('A data de liquidação deve ser posterior à data de operação, anterior ou igual à data de vencimento e igual ou posterior à data de reversão.'))
        if self.data_liquidacao < self.data_reversao and self.data_reversao is not None:
            raise ValidationError(_('A data de liquidação deve ser posterior à data de operação, anterior ou igual à data de vencimento e igual ou posterior à data de reversão.'))

    def clean_data_reversao(self):
        """
        Validação do campo data_reversao
        """
        if self.reversivel == True:
            if self.data_reversao is None:
                raise ValueError(_('Contrato de aluguel está marcado como reversível. É necessário informar a data de reversão.'))
            if self.data_reversao < self.data_operacao:
                raise ValidationError(_('A data de reversão deve ser posterior à data de operação do contrato de aluguel.'))

    def clean_quantidade(self):
        """
        Validação do campo quantidade
        """

        if self.quantidade < 0:
            raise ValidationError(_('Quantidade inválida. Insira uma quantidade positiva.'))

    def clean_taxa(self):
        """
        Validação do campo quantidade
        """
        self.taxa = decimal.Decimal(self.taxa).quantize(decimal.Decimal('1.000000'))
        if self.taxa < 0:
            raise ValidationError(_('Taxa inválida. Insira uma taxa positiva.'))

    def clean_preco(self):
        """
        Validação do campo preço
        """
        self.preco = decimal.Decimal(self.preco).quantize(decimal.Decimal('1.000000'))
        if self.preco < 0:
            raise ValidationError(_('Preço inválido. Insira uma preço positivo.'))

    def financeiro(self, data_referencia=datetime.date.today()):
        """ Datetime -> Decimal
        Calcula o valor financeiro de um contrato. Caso o contrato esteja
        liquidado, a data de referencia é igual à data de liquidação, caso
        contrário, a data de referência é a data de hoje.
        """
        if self.data_liquidacao == None:
            return round(self.preco * self.quantidade * ((1 + self.taxa/100) ** decimal.Decimal((self.calendario.dia_trabalho_total(self.data_operacao, data_referencia)/252))-1),2)
        else:
            return round(self.preco * self.quantidade * ((1 + self.taxa/100) ** decimal.Decimal((self.calendario.dia_trabalho_total(self.data_operacao, self.data_liquidacao)/252))-1),2)

    def renovar_boleta(self, quantidade, data_vencimento, data_renovacao):
        """ quantidade = int - quantidade a ser renovada.
            data_vencimento = datetime.date - nova data de vencimento
            data_renovacao = datetime.date - data de renovação do contrato
        Ao renovar um empréstimo, ele pode ser feito de duas maneiras:
            - Renovação completa, onde a data de vencimento é adiada. A parcela
            não renovada deve imediatamente ser liquidada
            - Renovação parcial, onde parte do contrato é liquidado e
            a outra parte é renovada, com sua data de vencimento adiada.
        """
        if data_vencimento > self.data_vencimento:
            # Renovação completa
            if quantidade == self.quantidade:
                self.data_vencimento = data_vencimento
                self.save()
            # Renovação parcial
            elif quantidade < self.quantidade:
                # Criando uma cópia da boleta:
                boleta_parcial_liquidada = self

                # Remove o ID, para que, ao salvar o contrato, salve como um novo contrato
                # com as informações relevantes atualizadas.
                boleta_parcial_liquidada.id = None
                boleta_parcial_liquidada.quantidade = self.quantidade - quantidade
                boleta_parcial_liquidada.data_liquidacao = data_renovacao
                boleta_parcial_liquidada.boleta_original = self.id
                boleta_parcial_liquidada.clean_taxa()
                boleta_parcial_liquidada.clean_preco()
                boleta_parcial_liquidada.full_clean()
                boleta_parcial_liquidada.save()
                # Liquidar a boleta

                self.data_vencimento = data_vencimento
                self.quantidade = quantidade
                boleta_parcial_liquidada.full_clean()
                self.save()
            # Quantidade inválida
            else:
                raise ValueError('Insira uma quantidade válida para renovação. Uma quantidade válida é menor que a quantidade total do contrato.')
        else:
            raise ValueError("Insira uma data de vencimento maior que a anterior.")

    def liquidar_boleta(self, quantidade, data_referencia=None):
        """
        quantidade - quantidade do ativo liquidado
        data_referencia - data de liquidação da boleta
        Uma liquidação gera uma movimentação negativa do
        ativo, para que a movimentação entre como um rendimento do ativo na
        avaliação do desempenho deste, sem alteração de quantidade do mesmo,
        e uma movimentação de entrada de caixa.
        Uma liquidação pode ser completa ou parcial. A liquidação completa
        implica na criação da movimentação de caixa e do ativo, e criação de um
        CPR a ser recebido em D+1 da liquidação. Na liquidação
        parcial, apenas uma parte das ações do contrato de aluguel são liquidadas.
        Isso separa a boleta em duas partes, a parte que foi liquidada e a parte
        que continua me vigência. A boleta original se torna a parte liquidada
        e uma nova boleta é criada para o restante das ações ainda alugadas.

        Como conseguimos ver as boletas liquidadas apenas no dia seguinte, a
        data_referencia padrão é D-1 de hoje.
        """
        # Como liquidamos
        if data_referencia == None:
            data_referencia = self.calendario.dia_trabalho(datetime.date.today(), -1)
        # Se houver data de reversão, data de liquidação deve ser maior ou
        # igual à data de reversão
        if self.reversivel == True and self.data_reversao is not None and data_referencia <= self.data_vencimento:
            # Data de liquidação deve ser maior que data de reversão
            if data_referencia >= self.data_reversao:
                if quantidade > 0:
                    if quantidade == self.quantidade:
                        # Liquidar completamente
                        # 1. Atualizar data de liquidação
                        self.data_liquidacao = data_referencia
                        print('Liquidação completa!')
                        self.save()
                        # Cria movimentação do ativo:
                        self.criar_movimentacao()
                        # Criar boleta de provisão de pagamento
                        self.criar_boleta_provisao()

                    elif quantidade < self.quantidade:
                        # Criar nova boleta de aluguel
                        nova_boleta = BoletaEmprestimo(ativo=self.ativo,
                            data_operacao=self.data_operacao,
                            fundo=self.fundo,
                            corretora=self.corretora,
                            data_vencimento=self.data_vencimento,
                            data_liquidacao=None,
                            reversivel=self.reversivel,
                            data_reversao=self.data_reversao,
                            operacao=self.operacao,
                            comissao=self.comissao,
                            quantidade=quantidade,
                            preco=self.preco,
                            taxa=round(self.taxa,6),
                            boleta_original=self.boleta_original,
                            caixa_alvo=self.caixa_alvo,
                            calendario=self.calendario,
                            custodia=self.custodia)
                        nova_boleta.full_clean()
                        nova_boleta.save()
                        nova_boleta.liquidar_boleta(quantidade, data_referencia)
                        # Liquidar boleta parcial
                        # Atualizar boleta com nova quantidade
                        self.quantidade -= quantidade
                        # Salvar alterações no banco de dados
                        self.save()

                    else:
                        # Erro - quantidade maior que a quantidade do contrato
                        raise ValueError("A quantidade a ser liquidada é maior que a quantidade do contrato. Insira uma quantidade válida.")
                else:
                    # Erro - quantidade não pode ser negativa
                    raise ValueError("A quantidade a ser liquidada deve ser maior que zero.")
            else:
                raise ValueError("A data de liquidação deve ser maior que a de reversão.")
        # Caso a boleta não seja reversível, o contrato deve ser carregado até o fim do termo.
        # No caso da liquidação em data de liquidação,
        elif data_referencia == self.data_liquidacao:
            pass
        elif self.data_reversao is None:
            raise ValueError("A boleta não possui data de reversão, apesar de ser reversível. Insira a data de reversão ou marque-a como não reversível.")
        # Erro: O contrato só pode ser liquidado ao final do termo
        else:
            raise ValueError('O contrato não é reversível, só é possível liquidá-lo no vencimento.')

    def fechar_boleta(self, data_referencia):
        """
        O fechamento da boleta deve ocorrer da seguinte maneira:
        DATA DA OPERAÇÃO:
            - Cria a boleta de CPR, com valor financeiro zero.
        DATAS ENTRE OPERAÇÃO E LIQUIDAÇÃO:
            - Atualiza a boleta de CPR com os juros acumulados no período.
        DATA DE LIQUIDAÇÃO:
            - Atualiza a data de pagamento da boleta para a data de liquidação.
            - Data de pagamento da boleta de CPR é atualizada
        """
        if data_referencia == self.data_operacao:
            self.criar_boleta_CPR()
        elif data_referencia > self.data_operacao and \
            (self.data_liquidacao == None or data_referencia < self.data_liquidacao):
            cpr = self.boleta_CPR.first()
            if cpr == None:
                self.criar_boleta_CPR()
                cpr = self.boleta_CPR.first()
            cpr.valor_cheio = self.financeiro(data_referencia=data_referencia)
            cpr.save()
        elif data_referencia == self.data_liquidacao:
            cpr = self.boleta_CPR.all().first()
            if cpr == None:
                self.criar_boleta_CPR()
                cpr = self.boleta_CPR.first()
            cpr.valor_cheio = self.financeiro(data_referencia=data_referencia)
            cpr.data_pagamento = self.data_liquidacao
            cpr.save()

    def criar_boleta_provisao(self):
        """
        Cria uma boleta de provisão de acordo com os parâmeteros da boleta
        de ação. Se já houver uma boleta de provisão criada, não há necessidade
        de criar outra.
        """
        # TODO: testar
        # Checar se já há boleta de provisão criada relacionada com esta.
        if self.boleta_provisao.all().exists() == False:
            # Criar boleta de provisão
            boleta_provisao = BoletaProvisao(
                descricao = "Aluguel de " + self.ativo.nome,
                caixa_alvo = self.caixa_alvo,
                fundo = self.fundo,
                # Pagamento em d+1 (padrão Brasil)
                data_pagamento = self.calendario.dia_trabalho(self.data_liquidacao, 1),
                # A movimentação de caixa tem sinal oposto à variação de quantidade
                financeiro = self.financeiro(self.data_liquidacao),
                content_object = self
            )
            boleta_provisao.save()

    def criar_boleta_CPR(self):
        """
        Cria uma boleta de CPR de acordo com os parâmeteros da boleta
        de ação. Se já houver uma boleta de CPR criada, não há necessidade
        de criar outra. O valor_cheio é atualizado no fechamento da boleta.
        """
        # Checar se há boleta de CPR já criada:
        if self.boleta_CPR.all().exists() == False:
            # Criar boleta de CPR
            boleta_CPR = BoletaCPR(
                descricao = 'Aluguel ' + self.ativo.nome,
                valor_cheio = 0,
                data_inicio = self.data_operacao,
                data_pagamento = self.data_vencimento,
                fundo = self.fundo,
                content_object = self,
                tipo = BoletaCPR.TIPO[3][0],
                capitalizacao = BoletaCPR.CAPITALIZACAO[2][0]
            )
            boleta_CPR.save()

    def criar_movimentacao(self):
        """
        A movimentação é criada quando a boleta é liquidada. Deve causar uma
        movimentação no ativo e no caixa do fundo.
        A movimentação é medida em financeiro do ativo.
        """
        # Checar se há movimentação já criada
        if self.relacao_movimentacao.all().exists() == False:
            # Criar Movimentacao do Ativo
            if self.data_liquidacao is not None:
                if self.data_liquidacao > self.data_operacao:
                    from fundo.models import Quantidade, Movimentacao
                    acao_movimentacao = Movimentacao(
                        # Valor da movimentação deve ser a contraparte da entrada
                        # de caixa. Desta maneira, o aluguel do ativo entra no cálculo
                        # da contribuição do ativo para a rentabilidade do fundo.
                        valor = -self.financeiro(),
                        fundo = self.fundo,
                        data = self.calendario.dia_trabalho(self.data_liquidacao, 1),
                        content_object = self,
                        objeto_movimentacao = self.ativo
                    )
                    acao_movimentacao.save()
                else:
                    raise ValueError("A boleta deve possuir uma data de liquidação válida.")
            else:
                raise TypeError("A data de liquidação deve estar preenchida para criar a movimentação.")

class BoletaCambio(BaseModel):
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
    data_operacao = models.DateField(default=datetime.date.today)
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
    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_cambio')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_cambio')

    def fechar_boleta(self):
        """
        Cria as boletas necessárias
        """
        self.criar_boleta_CPR_origem()
        self.criar_boleta_CPR_destino()
        self.criar_boleta_provisao_origem()
        self.criar_boleta_provisao_destino()

    def criar_boleta_CPR_origem(self):
        """
        Cria um CPR equivalente à moeda origem
        """
        if self.boleta_CPR.filter(descricao__contains='Caixa origem').exists() == False:
            cpr = BoletaCPR(
                descricao='Câmbio: Caixa origem: - ' + self.caixa_origem.nome,
                fundo=self.fundo,
                valor_cheio=decimal.Decimal(-abs(self.financeiro_origem)).quantize(decimal.Decimal('1.00')),
                data_inicio=self.data_operacao,
                data_pagamento=self.data_liquidacao_origem,
                content_object=self
            )
            cpr.full_clean()
            cpr.save()

    def criar_boleta_CPR_destino(self):
        """
        Cria um CPR equivalente à moeda de destino
        """
        if self.boleta_CPR.filter(descricao__contains='Caixa destino').exists() == False:
            cpr = BoletaCPR(
                descricao='Câmbio: Caixa destino - ' + self.caixa_destino.nome,
                fundo=self.fundo,
                valor_cheio=decimal.Decimal(abs(self.financeiro_final)).quantize(decimal.Decimal('1.00')),
                data_inicio=self.data_operacao,
                data_pagamento=self.data_liquidacao_destino,
                content_object=self
            )
            cpr.full_clean()
            cpr.save()

    def criar_boleta_provisao_origem(self):
        """
        Cria a boleta de provisão para o caixa origem.
        """
        if self.boleta_provisao.filter(descricao__contains='Caixa origem').exists() == False:
            provisao = BoletaProvisao(
                descricao='Câmbio: Caixa origem - ' + self.caixa_origem.nome,
                fundo=self.fundo,
                data_pagamento=self.data_liquidacao_origem,
                financeiro=decimal.Decimal(-abs(self.financeiro_origem)).quantize(decimal.Decimal('1.00')),
                caixa_alvo=self.caixa_origem,
                content_object=self
            )
            provisao.full_clean()
            provisao.save()

    def criar_boleta_provisao_destino(self):
        """
        Cria a boleta de provisão para o caixa destino.
        """
        if self.boleta_provisao.filter(descricao__contains='Caixa destino').exists() == False:
            provisao = BoletaProvisao(
                descricao="Câmbio: Caixa destino - " + self.caixa_destino.nome,
                fundo=self.fundo,
                data_pagamento=self.data_liquidacao_destino,
                financeiro=decimal.Decimal(abs(self.financeiro_final)).quantize(decimal.Decimal('1.00')),
                caixa_alvo=self.caixa_destino,
                content_object=self
            )
            provisao.full_clean()
            provisao.save()

class BoletaProvisao(BaseModel):
    """
    Boleta para registrar despesas a serem pagas por um fundo
    """

    ESTADO = (
        ("Pendente", "Pendente"),
        ("Liquidado", "Liquidado")
    )

    descricao = models.CharField("Descrição", max_length=50)
    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    data_pagamento = models.DateField()
    financeiro = models.DecimalField(max_digits=16, decimal_places=2)
    estado = models.CharField(max_length=9, choices=ESTADO, default=ESTADO[0][0])

    relacao_quantidade = GenericRelation('fundo.Quantidade', related_query_name='qtd_provisao')
    relacao_movimentacao = GenericRelation('fundo.Movimentacao', related_query_name='mov_provisao')

    # Content type para servir de ForeignKey de qualquer boleta a ser
    # inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Boletas de provisão"

    def fechado(self):
        """
        Determina se uma boleta de provisão foi fechada ou não.
        """
        return self.relacao_quantidade.exists() and self.relacao_movimentacao.exists()

    def fechar_boleta(self, data_referencia):
        """
        Executa as funções para o fechamento da boleta.
        Podemos verificar se a boleta está fechada pela existência de quantidade
        e movimentação relacionada.
        """
        self.criar_movimentacao()
        self.criar_quantidade()
        if self.data_pagamento == data_referencia:
            self.estado = self.ESTADO[1][0]

    def criar_movimentacao(self):
        """
        Cria a movimentação do caixa
        """
        if self.relacao_movimentacao.exists() == False:
            from fundo.models import Quantidade, Movimentacao
            mov = Movimentacao(
                valor=self.financeiro,
                fundo=self.fundo,
                data=self.data_pagamento,
                objeto_movimentacao=self.caixa_alvo,
                content_object=self
            )
            self.save()
            mov.full_clean()
            mov.save()

    def criar_quantidade(self):
        """
        Cria a quantidade do caixa.
        """
        if self.relacao_quantidade.exists() == False:
            from fundo.models import Quantidade, Movimentacao
            qtd = Quantidade(
                qtd=self.financeiro,
                fundo=self.fundo,
                data=self.data_pagamento,
                objeto_quantidade=self.caixa_alvo,
                content_object=self
            )
            self.save()
            qtd.full_clean()
            qtd.save()

class BoletaCPR(BaseModel):
    """
    Boleta para registrar CPR dos fundos.
    Acúmulo:
        Uma boleta de acúmulo de CPR serve incluir de forma gradual o efeito
        do pagamento de uma despesa ou recebimento de uma conta prevista para
        ser paga ou recebida pelo fundo.
    Diferimento:
        A boleta de diferimento tem uma função similar, mas de sentido diferente:
        enquanto que na boleta de acúmulo de CPR, o valor aumenta, de forma
        absoluta, gradualmente, até o valor estimado da despesa, enquanto que,
        no diferimento, há uma movimentação de caixa não prevista.
    CPR: Marca contrapartida de operações de ativos.
    Empréstimo: Marca o CPR de contratos de empréstimo de ativos.

        O fechamento de uma boleta de CPR cria, dependendo de seu tipo,
    quantidades e movimentações:
        - Acúmulo: Cria, diariamente, quantidades com seu valor, e na data de
    pagamento da boleta, a movimentação de saída do CPR.
        - Diferimento: Cria, na sua data de início, uma movimentação de entrada
    do CPR, com valor igual ao seu valor cheio e, diariamente, uma quantidade
    com seu valor.
        - CPR: Cria movimentações de entrada e saída na sua data de início e
    pagamento, respectivamente.
        - Empréstimo: Cria quantidades diariamente, igual ao valor do contrato
    no dia. Não cria nenhum tipo de movimentação.
    """

    # Tipo de CPR:
    # Diarização - o valor do CPR acumula de acordo com a capitalização
    # Diferimento - o valor é descontado pelo seu valor parcial
    # CPR - Não tem nenhum tipo de acúmulo ou desconto
    # Empréstimo - Apenas representa a quantidade e aluguel acumulada, não
    # deve criar nenhuma quantidade ou movimentação. A boleta de empréstimo é
    # atualizada diariamente, até o dia de sua liquidação.
    TIPO = (
        ("Acúmulo", "Acúmulo"),
        ('Diferimento', 'Diferimento'),
        ("CPR", "CPR"),
        ("Empréstimo", "Empréstimo"),
        ("Taxa de administração", "Taxa de administração")
    )

    # Capitalização - A diarização/diferimento afeta o valor do CPR na
    # periodicidade da capitalização. Capitalização mensal ocorre no último dia
    # útil do mês.
    CAPITALIZACAO = (
        ("Diária", "Diária"),
        ("Mensal", "Mensal"),
        ("Nenhuma", "Nenhuma")
    )

    TAXA_ADM_TEXTO = "TAXA DE ADMINISTRAÇÃO "

    # Descrição sobre o que é o CPR.
    descricao = models.CharField("Descrição", max_length=50)
    # Fundo relativo ao CPR
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    # Valor cheio do CPR. Assumimos que o valor final fica na moeda do fundo
    valor_cheio = models.DecimalField(max_digits=12, decimal_places=2,
        blank=True, null=True)
    # Valor parcial do CPR, no caso de boletar CPR que acumula diariamente.
    # Assumimos que o valor final fica na moeda do fundo.
    valor_parcial = models.DecimalField(max_digits=12, decimal_places=2,
        blank=True, null=True)
    # Data em que o CPR deve começar a ser considerado no fundo
    data_inicio = models.DateField()
    # Data de início da capitalização do CPR.
    data_vigencia_inicio = models.DateField(null=True, blank=True)
    # Data de fim da capitalização do CPR.
    data_vigencia_fim = models.DateField(null=True, blank=True)
    # Data em que o CPR deve sair da carteira.
    data_pagamento = models.DateField(null=True, blank=True, default=datetime.date.max)
    # Tipo de CPR
    tipo = models.CharField(max_length=21, choices=TIPO, default=TIPO[2][0])
    # Capitalização indica o período com que o CPR acumula
    capitalizacao = models.CharField(max_length=7, choices=CAPITALIZACAO,
        default=CAPITALIZACAO[2][0])

    relacao_vertice = GenericRelation('fundo.Vertice', related_query_name='cpr')
    relacao_provisao= GenericRelation('BoletaProvisao')
    # Content type para servir de ForeignKey de qualquer boleta de operação
    # a ser inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Boletas de CPR"

    def __str__(self):
        return '%s' % (self.descricao)

    def __repr__(self):
        return """
        BoletaCPR= <
            descricao={0},
            fundo={1},
            valor_cheio={2},
            valor_parcial={3},
            data_inicio={4},
            data_vigencia_inicio={5},
            data_vigencia_fim={6},
            data_pagamento={7},
            tipo={8},
            capitalizacao={9},
        >
        """.format(self.descricao, self.fundo, self.valor_cheio,
            self.valor_parcial, self.data_inicio, self.data_vigencia_inicio,
            self.data_vigencia_fim, self.data_pagamento, self.tipo,
            self.capitalizacao)

    def fechar_boleta(self, data_referencia):
        self.criar_vertice(data_referencia)

    def valor_presente(self, data_referencia):
        """
        Calcula o valor presente de uma boleta de CPR, dependendo de seu
        tipo, data de vigência e data de início e pagamento. No caso de
        CPR e Empréstimo, seu valor cheio é o seu valor presente, sempre
        """
        import pdb
        if self.tipo == self.TIPO[2][0] or self.tipo == self.TIPO[3][0]:
            cambio = self.buscar_cambio(data_referencia)
            return self.valor_cheio*cambio

        if self.valor_cheio == None and self.valor_parcial != None:
            self.valor_cheio = self.calcula_valor_cheio()
            self.save()
        elif self.valor_parcial == None and self.valor_cheio != None:
            self.valor_parcial = self.calcula_valor_parcial()
            self.save()
        # Tipo Acúmulo
        if self.tipo == self.TIPO[0][0]:
            # DIÁRIO

            if self.capitalizacao == self.CAPITALIZACAO[0][0]:
                if data_referencia > self.data_vigencia_fim:
                    # resultado = self.valor_cheio?
                    resultado = (self.fundo.calendario.dia_trabalho_total(self.data_vigencia_inicio, self.data_vigencia_fim))*self.valor_parcial
                    return resultado.quantize(decimal.Decimal('1.00'))
                elif data_referencia < self.data_vigencia_inicio:
                    return 0
                else:
                    resultado = (self.fundo.calendario.dia_trabalho_total(self.data_vigencia_inicio, data_referencia))*self.valor_parcial
                    return resultado.quantize(decimal.Decimal('1.00'))
            # Mensal
            elif self.capitalizacao == self.CAPITALIZACAO[1][0]:
                # Dentro da vigência
                if data_referencia >= self.data_vigencia_inicio and data_referencia <= self.data_vigencia_fim:
                    n_capitalizacoes = self.fundo.calendario.conta_fim_mes(self.data_vigencia_inicio, data_referencia)
                    print("N: " + str(n_capitalizacoes))
                    print("Iníco da vigência: " + str(self.data_vigencia_inicio))
                    print("Data de referência: " + str(data_referencia))
                    return n_capitalizacoes*self.valor_parcial
                elif data_referencia > self.data_vigencia_fim and data_referencia <= self.data_pagamento:
                    return self.fundo.calendario.conta_fim_mes(self.data_vigencia_inicio, self.data_vigencia_fim)*self.valor_parcial
        # Tipo Diferimento
        elif self.tipo == self.TIPO[1][0]:

            if self.capitalizacao == self.CAPITALIZACAO[0][0]:
                if data_referencia < self.data_vigencia_inicio:
                    return self.valor_cheio
                elif data_referencia > self.data_vigencia_fim:
                    return 0
                else:
                    return self.valor_cheio - self.valor_parcial*(self.fundo.calendario.dia_trabalho_total(self.data_vigencia_inicio, data_referencia)-1)
            elif self.capitalizacao == self.CAPITALIZACAO[1][0]:
                if self.data_vigencia_inicio <= data_referencia <= self.data_vigencia_fim:
                    return self.valor_cheio - self.valor_parcial*self.fundo.calendario.conta_fim_mes(self.data_vigencia_inicio, data_referencia)

    def buscar_cambio(self, data_referencia):
        """
        Dada uma data de referência, busca o câmbio relativo ao ativo do CPR.
        """
        if self.content_object != None:
            if type(self.content_object) != BoletaAcao and \
                type(self.content_object) != BoletaCambio and \
                type(self.content_object) != BoletaPassivo:
                moeda = self.content_object.ativo.moeda
                return self.fundo.cambio_do_dia(data_referencia, moeda)
            elif type(self.content_object) == BoletaAcao:
                moeda = self.content_object.acao.moeda
                return self.fundo.cambio_do_dia(data_referencia, moeda)
            else:
                return decimal.Decimal(1)
        else:
            """
            Corrigir isso depois
            """

            return decimal.Decimal(1)

    def calcula_valor_cheio(self):
        """
        Calcula o valor cheio de uma boleta baseado no valor parcial
        """
        if self.capitalizacao == self.CAPITALIZACAO[0][0]:
            cheio = self.valor_parcial * self.fundo.calendario.dia_trabalho_total(self.data_vigencia_inicio, self.data_vigencia_fim)
        elif self.capitalizacao == self.CAPITALIZACAO[1][0]:
            cheio = self.valor_parcial * self.fundo.calendario.conta_fim_mes(self.data_vigencia_inicio, self.data_vigencia_fim)
        return cheio

    def calcula_valor_parcial(self):
        """
        Calcula o valor parcial a partir do valor cheio
        """
        if self.capitalizacao == self.CAPITALIZACAO[0][0]:
            parcial = self.valor_cheio/self.fundo.calendario.dia_trabalho_total(self.data_vigencia_inicio, self.data_vigencia_fim)
        elif self.capitalizacao == self.CAPITALIZACAO[1][0]:
            parcial = self.valor_cheio/self.fundo.calendario.conta_fim_mes(self.data_vigencia_inicio, self.data_vigencia_fim)
        return parcial

    def criar_vertice(self, data_referencia):
        """
        Cria um vértice
        """
        if self.tipo == self.TIPO[0][0]:
            self.criar_vertice_acumulo(data_referencia)
        elif self.tipo == self.TIPO[1][0]:
            self.criar_vertice_diferimento(data_referencia)
        elif self.tipo == self.TIPO[2][0]:
            self.criar_vertice_CPR(data_referencia)
        elif self.tipo == self.TIPO[3][0]:
            self.criar_vertice_emprestimo(data_referencia)
        elif self.tipo == self.TIPO[4][0]:
            self.criar_vertice_taxa_adm(data_referencia)

    def criar_vertice_acumulo(self, data_referencia):
        """
        Cria um vértice
        """
        if self.relacao_vertice.filter(data=data_referencia).exists() == False:
            mov = 0
            if data_referencia == self.data_pagamento:
                # Na data de pagamento, o acúmulo deve ter uma movimentação contrária ao
                # seu valor presente para representar sua saída.
                mov = -self.valor_presente(data_referencia)

            vertice = fm.Vertice(
                fundo=self.fundo,
                custodia=self.encontrar_custodiante(),
                quantidade=1,
                valor=self.valor_presente(data_referencia),
                preco=1,
                movimentacao=mov,
                data=data_referencia,
                content_object=self
            )
            vertice.save()

    def criar_vertice_diferimento(self, data_referencia):
        """
        Vértice de diferimento:
            Movimentação de entrada
        """
        if self.relacao_vertice.filter(data=data_referencia).exists() == False:
            mov = 0

            if data_referencia == self.data_inicio:
                mov = self.valor_presente(data_referencia)

            vertice = fm.Vertice(
                fundo=self.fundo,
                custodia=self.encontrar_custodiante(),
                quantidade=1,
                preco=1,
                valor=self.valor_presente(data_referencia),
                movimentacao=mov,
                data=data_referencia,
                content_object=self
            )
            vertice.save()

    def criar_vertice_CPR(self, data_referencia):
        """
        Datas de movimentação: data de início e data de pagamento
        Datas de quantidade: data de início até D-1 da data de pagamento
        """
        if self.relacao_vertice.filter(data=data_referencia).exists() == False:
            mov = 0
            val = 0

            if data_referencia == self.data_inicio:
                mov = self.valor_presente(data_referencia) + mov
            if data_referencia == self.data_pagamento:
                mov = -self.valor_presente(data_referencia) + mov

            if data_referencia == self.data_pagamento:
                val = 0
            else:
                val = self.valor_presente(data_referencia)
            if mov != 0 or val != 0:
                # Necessário criar vértice apenas se algum dos valores não é zero.
                vertice = fm.Vertice(
                    fundo=self.fundo,
                    custodia=self.encontrar_custodiante(),
                    quantidade=1,
                    valor=val,
                    preco=1,
                    movimentacao=mov,
                    data=data_referencia,
                    content_object=self
                )

                vertice.save()

    def criar_vertice_emprestimo(self, data_referencia):

        if self.relacao_vertice.filter(data=data_referencia).exists() == False:
            val = 0

            if data_referencia == self.data_pagamento or data_referencia == self.data_inicio:
                val = 0
            else:
                val = self.valor_presente(data_referencia)
            vertice = fm.Vertice(
                fundo=self.fundo,
                custodia=self.encontrar_custodiante(),
                quantidade=1,
                valor=val,
                preco=1,
                movimentacao=0,
                data=data_referencia,
                content_object=self
            )
            vertice.save()

    def criar_vertice_taxa_adm(self, data_referencia):
        """
        Tratamento da taxa de administração:
            - Se a data referencia for maior que o início da vigência e menor ou
        igual à data final de vigencia, a taxa acumula.
                - Caso ela esteja no primeiro dia útil do mês, calcula o valor
            com base na carteira do último dia útil.
                - Caso ela esteja no meio do período de vigência, pega o valor
            cheio atual e soma a ele o valor da taxa de administração calculada
            com base no dia anterior.
            - Caso ela se encontre além do fim da data de vigência e antes da
        data de pagamento, ela permanece a mesma.
                - Cria uma provisão com o valor da taxa cheia, com data de
            pagamento igual à data de pagamento do CPR.

        """
        # Ainda não criou nenhum tipo de vértice. Evita double counting.
        if self.relacao_vertice.filter(data=data_referencia).exists() == False:
            # Capitalização diária.
            if self.capitalizacao == BoletaCPR.CAPITALIZACAO[0][0]:
                from dateutil.relativedelta import relativedelta
                """
                Checa se a data está dentro do intervalo da vigencia.
                """
                if data_referencia >= self.data_vigencia_inicio and \
                    data_referencia <= self.data_vigencia_fim:

                    cal = self.fundo.calendario
                    dia_anterior = cal.dia_trabalho(data_referencia, -1)
                    """
                    Checa se preciso criar acumular ou calcular a taxa do zero.
                    """
                    if data_referencia <= self.data_vigencia_fim and \
                        data_referencia > self.data_vigencia_inicio:
                        """
                        Calcula a taxa de administração e cria a provisão.
                        """
                        # Pega carteira do dia anterior. Não pego pela mais recente para que
                        # seja possível reprocessar a cota de um determinado dia.
                        carteira = fm.Carteira.objects.get(fundo=self.fundo, \
                            data=dia_anterior)
                        # Pega o vértice relativo ao dia anterior
                        content = ContentType.objects.get_for_model(BoletaCPR)
                        # Pega o valor da taxa pelo vértice, pois o valor da
                        # boleta é atualizado diariamente.
                        vertice_taxa_adm_anterior = fm.Vertice.objects.get(fundo=self.fundo,
                            data=dia_anterior, content_type=content,\
                            object_id=self.id)
                        taxa_acumulada = vertice_taxa_adm_anterior.valor

                        adm_dia = (carteira.pl_nao_gerido(dia_anterior)*self.fundo.taxa_administracao/100)/252
                        adm_dia.quantize(decimal.Decimal('1.00'))
                        adm_dia_min = self.fundo.taxa_adm_minima/cal.dias_uteis_mes(data_referencia)
                        taxa_acumulada = decimal.Decimal(-max(adm_dia_min, adm_dia) + taxa_acumulada).quantize(decimal.Decimal('1.00'))
                        self.valor_cheio = taxa_acumulada
                        self.save()
                        vertice = fm.Vertice(
                            fundo=self.fundo,
                            custodia=self.encontrar_custodiante(),
                            quantidade=1,
                            valor=taxa_acumulada,
                            preco=1,
                            movimentacao=0,
                            data=data_referencia,
                            content_object=self
                        )
                        vertice.save()

                    elif data_referencia == primeiro_dia_util_mes:
                        # Cria um vértice com a taxa de administração calculada
                        taxa_fundo = self.fundo.taxa_administracao/100
                        carteira = fm.Carteira.objects.get(fundo=self, data=cal.dia_trabalho(data_referencia, -1))
                        adm_dia = (carteira.pl*self.fundo.taxa_administracao/100)/252
                        adm_dia_min = self.fundo.taxa_adm_minima/cal.dias_uteis_mes(data_referencia)
                        taxa_adm = -decimal.Decimal(max(adm_dia, adm_dia_min)).quantize(decimal.Decimal('1.00'))

                        vertice = fm.Vertice(
                            fundo=self.fundo,
                            custodia=self.encontrar_custodiante(),
                            quantidade=1,
                            valor=taxa_adm,
                            preco=1,
                            movimentacao=0,
                            data=data_referencia,
                            content_object=self
                        )
                        vertice.save()

                elif data_referencia > self.data_vigencia_fim and \
                    data_referencia <= self.data_pagamento:
                    """
                    Se não é data do pagamento, não cria movimentação.
                    """
                    desc_prov = "Taxa de administração"
                    # Verifica se há provisão criada. Se não houver, cria uma.
                    if self.relacao_provisao.exists() == False:
                        prov_taxa_adm = Provisao(
                            descricao=self.TAXA_ADM_TEXTO,
                            caixa_alvo=self.fundo.caixa_padrao,
                            fundo=self.fundo,
                            data_pagamento=self.data_pagamento,
                            financeiro=self.valor_cheio,
                            estado=BoletaProvisao.ESTADO[0][0]
                        )
                    # Cria vértice.
                    if self.relacao_vertice.filter(data=data_referencia).exists() == False:
                        mov = 0
                        val = self.valor_cheio
                        if data_referencia == self.data_pagamento:
                            mov = -self.valor_cheio
                            val = 0
                        vertice = fm.Vertice(
                            fundo=self.fundo,
                            custodia=self.encontrar_custodiante(),
                            quantidade=1,
                            valor=val,
                            preco=1,
                            movimentacao=mov,
                            data=data_referencia,
                            content_object=self
                        )
                        vertice.save()

    def encontrar_custodiante(self):
        """
        Encontra quem é o custodiante do ativo relativo ao CPR
        """
        if type(self.content_object) != BoletaCambio and \
            type(self.content_object) != BoletaPassivo and \
            self.content_object != None:
            return self.content_object.custodia
        elif type(self.content_object) == BoletaCambio:
            if "origem" in self.descricao:
                return self.content_object.caixa_origem.custodia
            else:
                return self.content_object.caixa_destino.custodia
        elif type(self.content_object) == BoletaPassivo:
            return self.content_object.fundo.caixa_padrao.custodia
        elif self.content_object == None:
            return self.fundo.custodia

class BoletaPassivo(BaseModel):
    """
    Boleta de movimentação de passivo de fundos.
    Deve criar um certificado de passivo quando a boleta for cotizável.
    A boleta de passivo é responsável pela notação de informações relevantes
    de passivo e movimentações de caixa e cálculo de IR, se for o caso de
    resgate de cotista pessoa física.

    No período entre cotização e liquidação, o fundo deve possuir um CPR
    do tamanho da movimentação.

    Na data de cotização, o fundo deve emitir cotas (criar mais cotas -
    no caso de uma aplicação) ou consumir cotas (destruir cotas -
    no caso de um resgate).

    As cotas totais de um fundo deve ser igual ao somatório de cotas aplicadas
    de todos os certificados de passivo.
    """

    """
    TODO: ATUALIZAR BOLETA - CASO SEJA UMA BOLETA PROVENIENTE DE UMA OUTRA
    BOLETA DE FUNDOS, TENTA ATUALIZAR DE ACORDO COM O VALOR DA COTA NA
    BOLETA DE FUNDOS.
    """

    OPERACAO = (
        ('Aplicação', 'Aplicação'),
        ('Resgate', 'Resgate'),
        ('Resgate Total', 'Resgate Total')
    )

    cotista = models.ForeignKey('fundo.Cotista', on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    data_operacao = models.DateField()
    data_cotizacao = models.DateField()
    data_liquidacao = models.DateField()
    operacao = models.CharField(max_length=15, choices=OPERACAO)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    # Valor da cota do fundo
    cota = models.DecimalField(max_digits=15, decimal_places=8, null=True, blank=True)
    # Relaciona a boleta de passivo com todos os certificados de passivo gerados
    # ou consumidos.
    certificado_passivo = models.ManyToManyField('fundo.CertificadoPassivo',
        blank=True, null=True)

    # ForeignKey genérica para ligar com boletas de Aporte em fundo local ou offshore, quando for aplicável.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # GenericRelation para a boleta de CPR e provisão.
    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')

    def atualizar_boleta():
        """
        Busca informação de cota na boleta de origem, se tiver, ou no sistema,
        para atualizar a boleta com informação de cota.
        """
        if self.content_object == None and self.cota == None:
            # Se não há boleta de fundo que deu origem à boleta, assume que
            # devo buscar o valor da cota no sistema
            ativo = am.Ativo.objects.get(gestao=self)
            mm.Preco.objects.filter(ativo=self.ativo, data_referencia=self.data_cotizacao).first()

    def fechar_boleta(self):
        """
        Cria boletas de CPR e provisão.
        Se houver todas as informações, consome/cria um certificado de passivo.
        """
        self.criar_provisao()
        self.criar_boleta_CPR()
        if self.operacao == self.OPERACAO[0][0]:
            self.gerar_certificado()
        else:
            self.consumir_certificado()

    def criar_provisao(self):
        """
        Cria uma boleta de provisão de acordo com as informações na boleta.
        """
        if self.boleta_provisao.all().exists() == False:
            financeiro = abs(self.valor)
            if self.operacao == self.OPERACAO[0][0]:
                financeiro = abs(self.valor)
            else:
                financeiro = -abs(self.valor)
            provisao = BoletaProvisao(
                descricao=self.cotista.nome + ": " + self.operacao,
                caixa_alvo=self.fundo.caixa_padrao,
                fundo=self.fundo,
                data_pagamento=self.data_liquidacao,
                financeiro=financeiro,
                estado=BoletaProvisao.ESTADO[0][0],
                content_object=self
            )
            provisao.full_clean()
            provisao.save()

    def criar_boleta_CPR(self):
        """
        Cria uma boleta de provisão de acordo com as informações na boleta.
        Quatro casos possíveis para boletas de CPR:
        Resgate:
            - Data de cotização anterior à data de liquidação
            - Data de liquidação anterior à data de cotização
        Aplicação:
            - Data de cotização anterior à data de liquidação
            - Data de liquidação anterior à data de cotização
        O CPR possui um valor negativo nos seguintes cenários:
            - Aplicação - liquidação anterior à cotização
            - Resgate - cotização anterior à liquidação
        O CPR possui um valor positivo nos seguintes cenários:
            - Aplicação - cotização anteiror à liquidação
            - Resgate - liquidação anterior à cotização.
        """
        if self.boleta_CPR.all().exists() == False:
            financeiro = 0
            if (self.operacao == self.OPERACAO[0][0] and self.data_cotizacao < self.data_liquidacao) or \
                (self.operacao != self.OPERACAO[0][0] and self.data_liquidacao < self.data_cotizacao):
                financeiro = abs(self.valor)
                if self.data_cotizacao < self.data_liquidacao:
                    data_inicio = self.data_cotizacao
                    data_pagamento = self.data_liquidacao
                else:
                    data_inicio = self.data_liquidacao
                    data_pagamento = self.data_cotizacao
                cpr = BoletaCPR(
                    descricao=self.operacao + ": " + self.fundo.nome,
                    fundo=self.fundo,
                    valor_cheio=financeiro,
                    data_inicio=data_inicio,
                    data_pagamento=data_pagamento,
                    content_object=self
                )
            else:
                financeiro = -abs(self.valor)
                if self.data_cotizacao < self.data_liquidacao:
                    data_inicio = self.data_cotizacao
                    data_pagamento = self.data_liquidacao
                else:
                    data_inicio = self.data_liquidacao
                    data_pagamento = self.data_cotizacao
                cpr = BoletaCPR(
                    descricao=self.operacao + ": " + self.fundo.nome,
                    fundo=self.fundo,
                    valor_cheio=financeiro,
                    data_inicio=data_inicio,
                    data_pagamento=data_pagamento,
                    content_object=self
                )
            cpr.full_clean()
            cpr.save()

    def fechado(self):
        return self.boleta_provisao.exists() and self.boleta_CPR.exists() and \
            self.certificado_passivo.exists()

    def gerar_certificado(self):
        """
        Gera um certificado de passivo no fundo.
        """
        if (self.certificado_passivo.all().exists()==False) and self.cota != None:
            qtd = (self.valor/self.cota).quantize(decimal.Decimal('1.0000000'))
            certificado = fm.CertificadoPassivo(
                cotista=self.cotista,
                qtd_cotas=qtd,
                valor_cota=decimal.Decimal(self.cota).quantize(decimal.Decimal('1.000000')),
                cotas_aplicadas=qtd,
                data=self.data_cotizacao,
                fundo=self.fundo
            )
            certificado.full_clean()
            certificado.save()
            self.certificado_passivo.add(certificado)
            self.save()

    def consumir_certificado(self):
        """
        Deve buscar o certificado mais antigo que ainda tenha cotas a serem
        resgatadas e os resgata.
        """
        # Só consome os certificados se for possível calcular a quantidade de
        # cotas a serem consumidas - NO CASO DE RESGATE NÃO TOTAL.
        if (self.certificado_passivo.all().exists()==False and self.cota!=None and self.valor!=None and self.operacao==self.OPERACAO[1][0]):
            cotas_totais = abs(self.valor/self.cota)
            cotas_consumidas = cotas_totais
            while cotas_consumidas > 0:
                certificado_consumido = fm.CertificadoPassivo.objects.filter(cotas_aplicadas__gt=0,\
                    fundo=self.fundo).earliest('data')
                if cotas_consumidas > certificado_consumido.cotas_aplicadas:
                    cotas_consumidas -= certificado_consumido.cotas_aplicadas
                    certificado_consumido.cotas_aplicadas = 0
                else:
                    certificado_consumido.cotas_aplicadas = (certificado_consumido.cotas_aplicadas - cotas_consumidas).quantize(decimal.Decimal('1.0000000'))
                    cotas_consumidas = 0
                self.certificado_passivo.add(certificado_consumido)
                certificado_consumido.save()
                self.save()
        if (self.operacao == self.OPERACAO[2][0]):
            pass
