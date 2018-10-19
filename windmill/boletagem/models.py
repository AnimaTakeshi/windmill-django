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
import decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from fundo.models import Quantidade, Movimentacao
import ativos.models as am
import fundo.models as fm
import mercado.models as mm

# Create your models here.

class BoletaAcao(models.Model):
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
            acao_movimentacao = Movimentacao(
                valor = self.preco * self.quantidade + self.corretagem,
                fundo = self.fundo,
                data = self.data_operacao,
                content_object = self,
                objeto_movimentacao = self.acao
            )
            acao_movimentacao.full_clean()
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
    taxa = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True)
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
    preco = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    caixa_alvo = models.ForeignKey('ativos.Caixa', null=False, on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_fundo_local')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_fundo_local')
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
        if self.quantidade is None:
            if self.cota_disponivel() == True:
                if self.operacao == "Aplicação":
                    quantidade = abs(self.financeiro)/self.preco
                elif self.operacao == "Resgate":
                    quantidade = -abs(self.financeiro)/self.preco
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
        if self.passivo() == True and self.quantidade is not None:
            self.criar_boleta_passivo()

    def atualizar_boleta(self):
        """
        Busca informações no sistema para completar a boleta.
        """
        if self.preco is None:
            if self.cota_disponivel() == True:
                if self.quantidade is None and self.financeiro is not None:
                    self.quantidade = self.financeiro/self.preco
            self.clean_quantidade()

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
                object_id=self.id,
                objeto_movimentacao=self.ativo,
                tipo_id=self.ativo.id
            )
            print(self)
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
            qtd = fm.Quantidade(
                qtd=self.quantidade,
                fundo=self.fundo,
                data=self.data_cotizacao,
                content_object=self,
                object_id=self.id,
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
            if self.data_cotizacao < self.data_liquidacao:
                cpr = BoletaCPR(
                    descricao = self.operacao + " " + self.ativo.nome,
                    valor_cheio = self.financeiro,
                    data_inicio = self.data_cotizacao,
                    data_pagamento = self.data_liquidacao,
                    fundo = self.fundo,
                    content_object = self
                )
                cpr.save()
            else:
                cpr = BoletaCPR(
                    descricao = self.operacao + " " + self.ativo.nome,
                    valor_cheio = self.financeiro,
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
                financeiro= -self.financeiro,
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
                cotista = fm.Cotista(nome=self.fundo.nome)
                cotista.save()
            passivo = BoletaPassivo(
                cotista=cotista,
                valor=self.financeiro,
                data_movimentacao=self.data_operacao,
                data_cotizacao=self.data_cotizacao,
                data_liquidacao=self.data_liquidacao,
                operacao=self.operacao,
                fundo=self.ativo,
                cota=self.preco,
                content_object=self
            )
            passivo.full_clean()
            passivo.save()

class BoletaFundoOffshore(models.Model):
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

    """
    O estado da boleta é atualizado automaticamente, conforme a boleta é
    fechada dia a dia. A cada fechamento, deve ser verificado se houve
    divulgação do valor da cota, ou se houve liquidação da movimentação.
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
    estado = models.CharField(max_length=48, choices=ESTADO)
    data_operacao = models.DateField(default=datetime.date.today)
    data_cotizacao = models.DateField()
    data_liquidacao = models.DateField()
    financeiro = models.DecimalField(max_digits=16, decimal_places=6, blank=True, null=True)
    preco = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    quantidade = models.DecimalField(max_digits=15, decimal_places=6, blank=True, null=True)
    operacao = models.CharField(max_length=13, choices=OPERACAO)
    caixa_alvo = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)

    boleta_provisao = GenericRelation('BoletaProvisao', related_query_name='provisao')
    boleta_CPR = GenericRelation('BoletaCPR', related_query_name='CPR')
    relacao_quantidade = GenericRelation(Quantidade, related_query_name='qtd_fundo_off')
    relacao_movimentacao = GenericRelation(Movimentacao, related_query_name='mov_fundo_off')

    def clean_quantidade(self):
        """
        Valida o campo quantidade. Alinha o valor do campo com a operação
        realizada
        """
        if "Resgate" in self.operacao:
            self.quantidade = -abs(self.quantidade)
        else:
            self.quantidade = abs(self.quantidade)

    def fechado(self):
        """
        Determina se a boleta já foi fechada ou não.
        """
        if self.estado == "Concluído":
            return True
        else:
            return False

    def cotizavel(self):
        """
        Determina se é possível cotizar a boleta, calculando a quantidade de
        cotas que serão movimentadas na operação.
        """
        if mm.Preco.objects.filter(ativo=self.ativo, data_referencia=data_cotizacao).exists():
            return True
        return False

    def passivo(self):
        """
        Determina se a boleta
        """

    def fechar_boleta(self):
        """
        O fechamento deve pegar apenas as boletas que possuem o campo 'fechada'
        como Falso.
        Ao fazer o fechamento, devemos avaliar os seguintes casos:
        A boleta de provisão para a liquidação da movimentação deve ser criada
        indepentente de haver informação de cotização.

        Em caso de liquidação anterior à cotização:

        1 - Criar uma boleta de CPR de cotização, independente de haver ou não
        informação de cotização - a saída de caixa é a contraparte da entrada
        do CPR de cotização. A data de pagamento da boleta de CPR é igual à
        data de cotização da boleta.

        2 - Na data de cotização:
            - Se houver informação de cotização, criar a movimentação do ativo e
            a quantidade de variação do ativo.
            - Se não houver, deve ser criada uma boleta de CPR de movimentação
            a cotizar, com data de pagamento em aberto. A movimentação e
            quantidade do ativo devem ser criados quando há informação de
            cotização no sistema.

        Em caso de cotização anterior à liquidação:

        1 - Na data de cotização, há informação de valor de cota?
            - Caso não haja:
            Criar uma boleta de CPR para a pendencia da cotização com data de
            pagamento em aberto.
            Criar uma boleta de CPR para a pendência da liquidação.
            - Caso haja:
            Criar apenas a boleta de CPR de liquidação.

        """
        if self.fechada == False:
            if self.boleta_provisao.all().exists() == False:
                provisao = BoletaProvisao(
                    descricao=self.operacao + " de " + self.ativo.Nome,
                    caixa_alvo=self.caixa_alvo,
                    fundo=self.fundo,
                    data_pagamento=self.data_liquidacao,
                    financeiro=self.financeiro,
                    content_object=self
                )
                provisao.full_clean()
                provisao.save()
            if self.data_cotizacao < self.data_liquidacao:
                # TODO: Verificar se há preço de cotização para criar a quantidade
                # e movimentação.
                # Caso não haja, deve criar as duas boletas de CPR
                pass
            elif self.data_cotizacao >= self.data_liquidacao:
                # Criar boleta de CPR de cotização.
                # Verificar se a data de referencia para o fechamento.
                pass

    def criar_movimentacao(self):
        """
        Cria a movimentação do ativo. Deve ser criada no mesmo dia em que
        a quantidade do ativo é gerada, para que não haja descasamento da
        variação de quantidade e, no cálculo do retorno do ativo, não haja
        um retorno errado devido a esse descasamento
        """

    def criar_quantidade(self):
        pass

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
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
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
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name_plural = "Boletas de CPR"

    def __str__(self):
        return '%s' % (self.descricao)

class BoletaPassivo(models.Model):
    """
    Boleta de movimentação de passivo de fundos.
    """

    OPERACAO = (
        ('Aplicação', 'Aplicação'),
        ('Resgate', 'Resgate'),
        ('Resgate Total', 'Resgate Total')
    )

    cotista = models.ForeignKey('fundo.Cotista', on_delete=models.PROTECT)
    valor = models.DecimalField(max_digits=13, decimal_places=2)
    data_movimentacao = models.DateField()
    data_cotizacao = models.DateField()
    data_liquidacao = models.DateField()
    operacao = models.CharField(max_length=15, choices=OPERACAO)
    fundo = models.ForeignKey('ativos.Ativo', on_delete=models.PROTECT)
    cota = models.DecimalField(max_digits=15, decimal_places=6)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
