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
import decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from fundo.models import Quantidade, Movimentacao
import ativos.models as am
import fundo.models as fm

# Create your models here.

class BoletaAcao(models.Model):
    """
    Representa a boleta de um trade de ações.
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
        Não aceita preços negativos, apenas positivos
        """
        if self.preco < 0 :
            self.preco = -self.preco

    def save(self, *args, **kwargs):
        """
        Caso o valor da corretagem não tenha sido inserido, calcula.
        """
        self.clean()
        if self.corretagem == None:
            self.corretagem = self.corretora.calcular_corretagem(self.quantidade * self.preco, self.quantidade)
            super().save(*args, **kwargs)
        else:
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
                descricao = op + self.acao.nome,
                valor_cheio = -(self.preco * self.quantidade) + self.corretagem,
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
            acao_quantidade = Quantidade(
                qtd = self.quantidade,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_quantidade = self.acao
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
                valor = self.preco * self.quantidade + self.corretagem,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_movimentacao = self.acao
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
    data_liquidacao = models.DateField(null=True, blank=True)
    corretora = models.ForeignKey('fundo.Corretora', null=False, on_delete=models.PROTECT)
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
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_rfloc')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_rfloc')

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
            acao_movimentacao = Movimentacao(
                valor = round(self.preco * self.quantidade + self.corretagem, 2),
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_movimentacao = self.ativo
            )
            acao_movimentacao.save()

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
    corretagem = models.DecimalField(max_digits=8, decimal_places=2)
    fundo = models.ForeignKey('fundo.Fundo', null=False, on_delete=models.PROTECT)
    operacao = models.CharField('Compra/Venda', max_length=1, choices=OPERACAO)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    nominal = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    taxa = models.DecimalField(max_digits=6, decimal_places=4, blank=True, null=True)
    preco = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    # Caixa que será afetado pela operação
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    # Relações genéricas que permitem ligar a boleta de renda fixa offshore à
    # boletas de provisão, CPR, quantidade e movimentação.
    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_rfoff')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_rfoff')

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
        if self.preco < 0:
            raise ValidationError(_("Preço inválido, insira um valor positivo para o preço."))

    def criar_movimentacao(self):
        """
        Cria uma movimentação do ativo relacionada a essa boleta, apenas se
        a boleta não possuir nenhuma movimentação ligada a ela
        """
        if self.relacao_movimentacao.all().exists() == False:
            ativo_movimentacao = fm.Movimentacao(
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
            ativo_quantidade = fm.Quantidade(
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
    financeiro = models.DecimalField(max_digits=16, decimal_places=6, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    preco = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_fundo_local')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_fundo_local')

    def clean_financeiro(self):
        """
        Valida o campo financeiro. Caso quantidade e preço estejam preenchidos,
        financeiro deve ser calculado como sendo igual a preço * quantidade.
        Caso algum dos dois não esteja preenchido, financeiro deve estar.
        """
        if self.quantidade == None or self.preco == None:
            if self.financeiro == None:
                raise ValidationError(_("Informe o financeiro ou quantidade e preço."))
        elif self.quantidade != None and self.preco != None:
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
        Alinha a quantidade com a operação.
        """
        if self.operacao == "Aplicação" and self.quantidade is not None:
            self.quantidade = abs(self.quantidade)
            self.clean_financeiro()
        elif "Resgate" in self.operacao and self.quantidade is not None:
            self.quantidade = -abs(self.quantidade)
            self.clean_financeiro()

    def criar_movimentacao(self):
        """
        Cria uma movimentação do ativo movimentado.
        """
        if self.relacao_movimentacao.all().exists() == False:
            self.clean_financeiro()
            mov = fm.Movimentacao(
                valor=self.financeiro,
                fundo=self.fundo,
                data=self.data_cotizacao,
                content_object=self,
                objeto_movimentacao=self.ativo
            )
            mov.clean()
            mov.save()


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
    data_operacao = models.DateField(default=datetime.date.today)
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
    # TODO: PARTE DE CPR.
    OPERACAO = (
        ('Doador', 'Doador'),
        ('Tomador', 'Tomador')
    )

    ativo = models.ForeignKey('ativos.Acao', on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    corretora = models.ForeignKey('fundo.Corretora', on_delete=models.PROTECT)
    data_vencimento = models.DateField()
    data_liquidacao = models.DateField(null=True, blank=True)
    reversivel = models.BooleanField()
    data_reversao = models.DateField(null=True, blank=True)
    operacao = models.CharField('Operação', max_length=10, choices=OPERACAO)
    comissao = models.DecimalField(max_digits=9, decimal_places=6)
    quantidade = models.DecimalField(max_digits=15, decimal_places=6)
    taxa = models.DecimalField(max_digits=8, decimal_places=6)
    preco = models.DecimalField(max_digits=10, decimal_places=6)
    boleta_original = models.ForeignKey('self', on_delete=models.PROTECT, null=True, blank=True)
    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    calendario = models.ForeignKey('calendario.Calendario',
        on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_emprestimo')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_emprestimo')

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

        if self.taxa < 0:
            raise ValidationError(_('Taxa inválida. Insira uma taxa positiva.'))

    def clean_preco(self):
        """
        Validação do campo preço
        """

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
                boleta_parcial_liquidada.save()
                # Liquidar a boleta

                self.data_vencimento = data_vencimento
                self.quantidade = quantidade
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
        if self.reversivel == True and self.data_reversao is not None:
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
                            calendario=self.calendario)
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
        elif data_referencia == self.data_liquidacao:
            pass
        elif self.data_reversao is None:
            raise ValueError("A boleta não possui data de reversão, apesar de ser reversível. Insira a data de reversão ou marque-a como não reversível.")
        # Erro: O contrato só pode ser liquidado ao final do termo
        else:
            raise ValueError('O contrato não é reversível, só é possível liquidá-lo no vencimento.')

    def fechar_boleta(self):
        """
        O fechamento de uma boleta de empréstimo acumula o CPR de aluguel.
        Cria apenas uma quantidade de CPR.
        """

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

    descricao = models.CharField("Descrição", max_length=50)
    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    data_pagamento = models.DateField()
    financeiro = models.DecimalField(max_digits=20, decimal_places=2)

    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_provisao')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_provisao')

    # Content type para servir de ForeignKey de qualquer boleta a ser
    # inserida no sistema.
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Boletas de provisão"

class BoletaCPR(models.Model):
    """
    Boleta para registrar CPR dos fundos.
    """
    # Descrição sobre o que é o CPR.
    descricao = models.CharField("Descrição", max_length=50)
    # Fundo relativo ao CPR
    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.PROTECT)
    # Valor cheio do CPR.
    valor_cheio = models.DecimalField(max_digits=12, decimal_places=2,
        blank=True, null=True)
    # Valor parcial do CPR, no caso de boletar CPR que acumula diariamente
    valor_diario = models.DecimalField(max_digits=12, decimal_places=2,
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
    data = models.DateField()
    # Preço do ativo.
    preco = models.DecimalField(max_digits=13, decimal_places=6)
    # Tipo de preço - Mercado, fechamento, contábil, gerencial,
    # tipo = models.CharField - limitar escolhas pelas colunas do modelo Preço

    class Meta:
        unique_together = (('ativo', 'data'),)

class BoletaPassivo(models.Model):
    pass
