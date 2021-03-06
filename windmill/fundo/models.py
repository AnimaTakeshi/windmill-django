"""
Modelos deste app servem para armazenar informações e processar eventos de
fundos geridos.
Responsabilidades deste app:
    - Executar funções relacionadas ao fundo:
        - Fechamento diário para cálculo de cota.
        - Fechamento mensal para cálculo de cota.

PROCESSO DE CÁLCULO DA COTA:
    1) Fechamento das boletas: As boletas devem ser fechadas para gerar as
quantidades e movimentações correspondentes.
    2)
"""
import decimal
from django.utils import timezone
from django.db import models
from django.db.models import Sum
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from phonenumber_field.modelfields import PhoneNumberField
import pandas as pd
import datetime

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
#
class BaseModel(models.Model):
    """
    Classe base para criar campos comuns a todas as classes, como 'criado em'
    ou 'atualizado em'
    """
    deletado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    # objects = BaseModelManager()
    # all_objects    = BaseModelManager(alive_only=False)

    class Meta:
        abstract = True

    # def delete(self):
    #     self.deletado_em = timezone.now()
    #     self.save()
    #
    # def hard_delete(self):
    #     super(BaseModel, self).delete()

class Fundo(BaseModel):
    """
    Descreve informações relevantes para um fundo.
    TODO: INSERIR DATA DE EXERCÍCIO SOCIAL
    TODO: CRIAR CPR E PROVISÃO DE PROVENTOS
    TODO: ZERAGEM DE CAIXA
    """
    # Categorias do fundo.
    CATEGORIAS = (
        ("Fundo de Ações", "Fundo de Ações"),
        ("Fundo Multimercado", "Fundo Multimercado"),
        ("Fundo Imobiliário", "Fundo Imobiliário"),
        ("Fundo de Renda Fixa", "Fundo de Renda Fixa"),
        ("Fundo de Participações", "Fundo de Participações")
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
    categoria = models.CharField("Categoria do Fundo", max_length=40,
    # para determinação da metodologia de cálculo do IR.
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
    # Taxa de administração mínima, de acordo com o regulamento do fundo.
    taxa_adm_minima = models.DecimalField('Taxa de Administração Mínima',
        max_digits=9, decimal_places=2, default=0)
    # Indica de quanto em quanto tempo a taxa de administração é apurada
    # No caso dos fundos locais, como a carteira é diária, a taxa de
    # administração é acumulada diariamente, com base no PL do dia anterior.
    # No caso de fundos offshore, com carteiras mensais, a taxa é calculada
    # mensalmente, com base no PL de fim do mês.
    capitalizacao_taxa_adm = models.CharField(max_length=15,
        choices=CAPITALIZACAO, null=True, blank=True)
    # Caixa padrão é o caixa em que o fundo recebe aportes. Quando há
    # movimentação de caixa sem caixa especificado, o caixa padrão é usado
    caixa_padrao = models.ForeignKey('ativos.Caixa', on_delete=models.PROTECT)
    # Indica qual calendário o fundo segue.
    calendario = models.ForeignKey('calendario.Calendario', on_delete=models.PROTECT)
    # indica quando terminará o próximo exercício social do fundo.
    data_exercicio_social = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'Fundos'

    def __str__(self):
        return '%s' % (self.nome)

    def verificar_proventos(self, data_referencia):
        """
        Verifica se há novos proventos de acordo com os ativos na carteira do dia anterior.
        1) Verifica se há novos proventos com ex-date igual à data de referência.
        2) Verifica se, dentre os ativos que possuem proventos, há algum que
        pertença à carteira do dia anterior.
        3) Se encontrar algum ativo, processa o provento de acordo:
            1) Dividendos e Juros sobre Capital Próprio
                Cria uma boleta de CPR e provisão de acordo
            2) Stock Split/stock dividend
                Cria quantidades de acordo
            3) Stock Inplit
                Cria uma quantidade negativa
            4) Direitos de subscrição
                Cria uma quantidade do direito de subscrição.
        """
        from mercado import models as mm
        from ativos import models as am
        from boletagem import models as bm
        import math

        proventos = mm.Provento.objects.filter(data_ex=data_referencia)
        if proventos:
            # Pega carteira do dia anterior como referência.
            carteira = Carteira.objects.get(data=self.calendario.dia_trabalho(data_referencia, -1), fundo=self)
            acoes = []
            vertices = []
            for vertice in carteira.vertices.all():
                if type(vertice.content_object) == am.Acao:
                    acoes.append(vertice.content_object)
                    vertices.append(vertice)
            for provento in proventos:
                if provento.ativo in acoes:
                    vertice = vertices[acoes.index(provento.ativo)]
                    # Dividendos/JSCP
                    if provento.tipo_provento == mm.Provento.TIPO[0][0] or provento.tipo_provento == mm.Provento.TIPO[1][0]:
                        # Cria CPR
                        CPR = bm.BoletaCPR(
                            descricao = provento.tipo_provento + " " + provento.ativo.nome + " ",
                            valor_cheio = vertice.quantidade * provento.valor_liquido,
                            data_inicio = data_referencia,
                            data_pagamento = provento.data_pagamento,
                            fundo = vertice.fundo,
                            content_object = provento
                        )
                        CPR.save()
                        # Cria Provento
                        # Busca caixa onde o provento será pago
                        caixa = am.Caixa.objects.get(custodia=vertice.custodia,\
                            corretora=vertice.corretora)
                        provisao = bm.BoletaProvisao(
                            descricao = provento.tipo_provento + " " + provento.ativo.nome + " ",
                            caixa_alvo = caixa,
                            fundo = vertice.fundo,
                            data_pagamento = provento.data_pagamento,
                            financeiro =  vertice.quantidade * provento.valor_liquido,
                            content_object = provento,
                        )
                        provisao.save()
                        # Cria movimentação do ativo, em contrapartida ao CPR
                        mov = Movimentacao(
                            valor = -abs(decimal.Decimal(vertice.quantidade * provento.valor_liquido).quantize(decimal.Decimal('1.000000'))),
                            fundo = vertice.fundo,
                            data = data_referencia,
                            content_object = provento,
                            objeto_movimentacao = provento.ativo
                        )
                        mov.full_clean()
                        mov.save()
                    # Stock Split/Stock dividend/Inplit
                    elif provento.tipo_provento == mm.Provento.TIPO[2][0] or \
                        provento.tipo_provento == mm.Provento.TIPO[4][0]:
                        qtd = Quantidade(
                            qtd = math.floor((provento.valor_bruto - 1) * vertice.quantidade),
                            fundo = vertice.fundo,
                            data = provento.data_ex,
                            content_object = provento,
                            objeto_quantidade = provento.ativo,
                        )
                        qtd.save()
                    # Direito de subscrição

    def zeragem_de_caixa(self, data_referencia):
        """
        Caso o caixa faça zeragem (investe em um fundo/compromissada para não
        deixar dinheiro parado), cria uma boleta de provisão indicando o
        quanto foi pago pela zeragem.
        """
        # Verifica se há caixa no dia anterior.
        import ativos.models as am
        import configuracao.models as cm
        caixas_zeragem = cm.ConfigZeragem.objects.filter(fundo=self)
        data_anterior = self.calendario.dia_trabalho(data_referencia, -1)
        tipo_caixa = ContentType.objects.get_for_model(am.Caixa)
        vertices_caixa = Vertice.objects.filter(content_type=tipo_caixa, \
            data=data_anterior)

        for vertice in vertices_caixa:
            if caixas_zeragem.filter(caixa=vertice.content_object):
                import boletagem.models as bm
                zeragem = caixas_zeragem.get(caixa=vertice.content_object).indice_zeragem
                nome_boleta = "Zeragem " + vertice.content_object.nome
                # Se a boleta de zeragem ainda não foi feita, cria a boleta
                if bm.BoletaProvisao.objects.filter(descricao__contains=nome_boleta, \
                    data_pagamento=data_referencia).exists() == False:
                    retorno = zeragem.retorno_do_periodo(data_anterior, data_referencia)
                    financeiro_zeragem = retorno*vertice.quantidade
                    provisao = bm.BoletaProvisao(
                        descricao=nome_boleta,
                        caixa_alvo=vertice.content_object,
                        fundo=self,
                        data_pagamento=data_referencia,
                        financeiro=decimal.Decimal(financeiro_zeragem).quantize(decimal.Decimal('1.00')),
                        estado=bm.BoletaProvisao.ESTADO[2][0]
                    )
                    provisao.full_clean()
                    provisao.save()

    """
    Fechamento do fundo
    """

    def fechar_fundo(self, data_referencia):
        """
        FECHAMENTO DE FUNDO
        Para fazer o fechamento de um fundo em uma determinada data de referência, é
        preciso:
            - Verificar, no app Mercado, se há algum provento cuja ex-date seja na
        data de referência. Se houver o ativo na carteira, deve processar o provento
        de forma apropriada:
                - Dividendo/JSCP:
                    - Cria uma movimentação no ativo na data_ex
                    - Criar um CPR com data de início na data ex e data de pagamento
                    igual à data de pagamento do provento.
                    - Cria uma provisão com data de pagamento igual à data de pagamento
                    do provento, e valor financeiro igual ao valor bruto por ação *
                    quantidade de ações na data com do provento.
                - Bonificação em ações:
                    - Cria uma quantidade do ativo na data de pagamento do provento
                    igual a (valor bruto - 1) * quantidade na data com do provento.
                - Direitos de subscrição:
                    - Cria uma quantidade do ativo representante do direito de
                    subscrição na data ex do provento.
                    - No momento em que a subscrição for paga, cria a movimentação de
                    entrada do ativo e boleta de provisão para a saída de caixa para
                    pagamento.
            - Fechar todas as boletas do fundo que ainda não foram fechadas.
            - Reunir todas as quantidades com data menor ou igual que a data de
        referência, e movimentações com data igual à data de referência, e
        criar vértices para o fundo.
            - Reunir todos os vértices referentes ao fundo na data de referencia.

            - Reunir todas as quantidades referentes ao fundo, com data igual ou
        anterior à data de referência. Quantidades são cumulativas. Consolidar
        e descartar aqueles que ficarem zerados (seria possível verificar
        através da comparação das quantidades que estava presentes no vértice do
        dia anterior.)
            - Reunir todas as movimentações referentes ao fundo, com data igual
        à data de referência. Movimentações são pontuais.
            - Reunir todas as boletas de CPR com data de início inferior ou igual à data de
        referência e data de pagamento superior ou igual à data de referência. Se boletas de
        CPR criarem movimentações e quantidades, não haverá necessidade de reunir
        as boletas, pois seus efeitos já seriam sentidos pelas quantidades e
        movimentações.
            - Cálculo da cota, considerando PL e movimentações feitas.
            - Atualização do número de cotas, caso tenha havido uma alteração
        devido à movimentação.
        """
        self.zeragem_de_caixa(data_referencia)
        self.fechar_boletas_do_fundo(data_referencia)
        self.criar_vertices(data_referencia)

    def fechar_boletas_do_fundo(self, data_referencia):
        """
        Reúne todas as boletas relevantes para a data de referência e faz seu
        fechamento.
        """
        print("Fechamento: " + data_referencia.strftime('%d/%m/%Y'))
        self.fechar_boletas_acao(data_referencia)
        self.fechar_boletas_cambio(data_referencia)
        self.fechar_boletas_rf_off(data_referencia)
        self.fechar_boletas_rf_local(data_referencia)
        self.fechar_boletas_emprestimo(data_referencia)
        self.fechar_boletas_fundo_local(data_referencia)
        self.fechar_boletas_fundo_offshore(data_referencia)
        self.fechar_boletas_fundo_local_como_ativo(data_referencia)
        self.fechar_boletas_fundo_off_como_ativo(data_referencia)
        self.fechar_boletas_passivo(data_referencia)

        """
        Conferêcia de carteira para verificar dividendos
        """

        self.fechar_boletas_CPR(data_referencia)
        self.fechar_boletas_provisao(data_referencia)

    def fechar_boletas_acao(self, data_referencia):
        """
        Pega todas as boletas de ação do fundo, para a data de referência, e
        executa o fechamento delas. Resultado esperado - Criação de quantidades,
        movimentações e vértice do CPR
        """
        from boletagem.models import BoletaAcao
        boletas = BoletaAcao.objects.filter(fundo=self, data_operacao=data_referencia)
        if boletas:
            for boleta in boletas:
                boleta.fechar_boleta()

    def fechar_boletas_rf_local(self, data_referencia):
        from boletagem.models import BoletaRendaFixaLocal
        for boleta in BoletaRendaFixaLocal.objects.filter(fundo=self, data_operacao=data_referencia):
            boleta.fechar_boleta()

    def fechar_boletas_rf_off(self, data_referencia):
        from boletagem.models import BoletaRendaFixaOffshore
        for boleta in BoletaRendaFixaOffshore.objects.filter(fundo=self,\
            data_operacao=data_referencia):
            boleta.fechar_boleta()

    def fechar_boletas_fundo_local(self, data_referencia):
        from boletagem.models import BoletaFundoLocal
        # Busca as boletas que possuem cotização anterior à liquidação
        for boleta in BoletaFundoLocal.objects.filter(fundo=self, \
            data_cotizacao__lte=data_referencia, \
            data_liquidacao__gte=data_referencia):
            boleta.fechar_boleta()

        # Busca as boletas que possuem data de liquidação anterior à cotização.
        for boleta in BoletaFundoLocal.objects.filter(fundo=self, \
            data_cotizacao__gte=data_referencia, \
            data_liquidacao__lte=data_referencia):
            boleta.fechar_boleta()

    def fechar_boletas_fundo_local_como_ativo(self, data_referencia):
        """
        Busca BoletaFundoLocal em que o ativo negociado é o fundo
        """
        from boletagem.models import BoletaFundoLocal
        from ativos.models import Fundo_Local
        # Busca o ativo correspondente ao fundo local
        fundo = Fundo_Local.objects.filter(gestao=self)
        if fundo.count() > 0:
            fundo = fundo[0]
            for boleta in BoletaFundoLocal.objects.filter(ativo=fundo, \
                data_cotizacao__lte=data_referencia, \
                data_liquidacao__gte=data_referencia):
                boleta.fechar_boleta()

            for boleta in BoletaFundoLocal.objects.filter(ativo=fundo, \
                data_cotizacao__gte=data_referencia, \
                data_liquidacao__lte=data_referencia):
                boleta.fechar_boleta()

    def fechar_boletas_fundo_offshore(self, data_referencia):
        from boletagem.models import BoletaFundoOffshore
        for boleta in BoletaFundoOffshore.objects.filter(fundo=self).\
            exclude(estado=BoletaFundoOffshore.ESTADO[5][0]):
            boleta.fechar_boleta(data_referencia)

    def fechar_boletas_fundo_off_como_ativo(self, data_referencia):
        """
        Busca BoletaFundoOffshore em que o ativo negociado é o fundo
        """
        from boletagem.models import BoletaFundoOffshore
        from ativos.models import Fundo_Offshore
        # Busca o ativo correspondente ao fundo local
        fundo = Fundo_Offshore.objects.filter(gestao=self).first()

        for boleta in BoletaFundoOffshore.objects.filter(ativo=fundo, \
            data_cotizacao__lte=data_referencia, \
            data_liquidacao__gte=data_referencia):
            boleta.fechar_boleta()

        for boleta in BoletaFundoOffshore.objects.filter(ativo=fundo, \
            data_cotizacao__gte=data_referencia, \
            data_liquidacao__lte=data_referencia):
            boleta.fechar_boleta()

    def fechar_boletas_passivo(self, data_referencia):
        from boletagem.models import BoletaPassivo
        boletas_passivo = BoletaPassivo.objects.filter(fundo=self, \
            data_cotizacao__gte=data_referencia)
        if boletas_passivo:
            for boleta in boletas_passivo:
                boleta.fechar_boleta()

    def fechar_boletas_emprestimo(self, data_referencia):
        """
        Deve pegar todas as boletas que não possuem data de liquidação e
        boletas cuja data de liquidação é igual à data de referência.
        """
        from boletagem.models import BoletaEmprestimo
        for boleta in BoletaEmprestimo.objects.filter(fundo=self, \
            data_liquidacao=None):
            boleta.fechar_boleta(data_referencia)

    def fechar_boletas_cambio(self, data_referencia):
        from boletagem.models import BoletaCambio
        for boleta in BoletaCambio.objects.filter(fundo=self, \
            data_operacao=data_referencia):
            boleta.fechar_boleta()

    def fechar_boletas_CPR(self, data_referencia):
        from boletagem.models import BoletaCPR
        for boleta in BoletaCPR.objects.filter(fundo=self, \
            data_inicio__lte=data_referencia, \
            data_pagamento__gte=data_referencia):
            boleta.fechar_boleta(data_referencia)

    def fechar_boletas_provisao(self, data_referencia):
        from boletagem.models import BoletaProvisao
        # Busca boletas com estado pendente.
        for boleta in BoletaProvisao.objects.filter(fundo=self):
            if boleta.fechado() == False:
                boleta.fechar_boleta(data_referencia)

    """
    Criação de vértices:
        - Juntar todos as quantidades com data menor ou igual à data de
        fechamento. Descartar aquelas que possuem quantidade total 0.
        - Juntar todas as movimentações com data igual à data de fechamento.
    """

    def juntar_quantidades(self, data_referencia):
        """ datetime -> DataFrame
        Junta as quantidades dos diferentes tipos de ativos e retorna o
        dataframe com todos os ativos.
        """
        import ativos.models as am

        tipo_objeto = ContentType.objects.get_for_model(am.Acao)
        carteira = self.juntar_quantidades_ativo(data_referencia, tipo_objeto)

        tipo_objeto = ContentType.objects.get_for_model(am.Renda_Fixa)
        carteira = carteira.append(self.juntar_quantidades_ativo(data_referencia, tipo_objeto))

        tipo_objeto = ContentType.objects.get_for_model(am.Caixa)
        carteira = carteira.append(self.juntar_quantidades_ativo(data_referencia, tipo_objeto))

        tipo_objeto = ContentType.objects.get_for_model(am.Fundo_Local)
        carteira = carteira.append(self.juntar_quantidades_ativo(data_referencia, tipo_objeto))

        tipo_objeto = ContentType.objects.get_for_model(am.Fundo_Offshore)
        carteira = carteira.append(self.juntar_quantidades_ativo(data_referencia, tipo_objeto))

        return carteira

    def juntar_quantidades_ativo(self, data_referencia, object_type):
        """ datetime -> DataFrame
        Busca, no banco de dados, todas as quantidades de um tipo de ativo
        com data menor ou igual à data de referência, e devolve
        as quantidades.
        """
        import ativos.models as am
        pd.set_option('display.max_columns', 10)
        """
        Preciso buscar todas as quantidades sem consolidá-las
        """
        # resultado = Quantidade.objects.filter(data__lte=data_referencia, \
        # fundo=self, tipo_quantidade=object_type).\
        # values('tipo_id', 'data', 'fundo').annotate(posicao=Sum('qtd'))
        resultado = Quantidade.objects.filter(data__lte=data_referencia, \
        fundo=self, tipo_quantidade=object_type)

        if resultado:
            """
            Buscando as informações de custódia de cada ativo
            """
            import boletagem.models as bm
            dicionario_boleta_custodia = []
            for qtd in resultado:
                if type(qtd.content_object) != bm.BoletaProvisao:
                    if type(qtd.content_object) == bm.BoletaAcao or \
                        type(qtd.content_object) == bm.BoletaRendaFixaLocal or \
                        type(qtd.content_object) == bm.BoletaRendaFixaOffshore:
                        dicionario_boleta_custodia.append({'id':qtd.id, \
                            'custodia_id':qtd.content_object.custodia_id, \
                            'corretora_id':qtd.content_object.corretora.id})
                    else:
                        dicionario_boleta_custodia.append({'id':qtd.id, \
                        'custodia_id':qtd.content_object.custodia_id, \
                        'corretora_id':qtd.content_object.caixa_alvo.corretora.id})

                else:
                    # Caso seja uma boleta de provisão
                    dicionario_boleta_custodia.append({'id':qtd.id, \
                    'custodia_id':qtd.content_object.caixa_alvo.custodia.id, \
                    'corretora_id':qtd.content_object.caixa_alvo.corretora.id})
            # Dataframe de boletas com custódia
            # Possui id_quantidade(id), id_custodia
            custodia = pd.DataFrame(dicionario_boleta_custodia)
            # Possui id_quantidade(id), id_ativo(tipo_id)
            resultado = pd.DataFrame(list(resultado.values('id', 'tipo_id', 'object_id', 'qtd', 'fundo', 'tipo_quantidade_id')))
            # Possui id_ativo (id)
            ativos = pd.DataFrame(list(am.Ativo.objects.all().values('id', 'nome', 'moeda')))
            # Juntando quantidades com suas respectivas corretoras e custódias
            resultado = resultado.merge(custodia, right_on='id', left_on='id')
            # Juntando quantidades com os nomes das ações.
            """
            Este último join abaixo pode vir a ser removido futuramente.
            """
            resultado = resultado.merge(ativos, right_on='id', \
                left_on='tipo_id').drop(['id_y', 'object_id'], axis=1)

            resultado['data'] = data_referencia

            return resultado
        else:
            return pd.DataFrame()

    def juntar_movimentacoes(self, data_referencia):
        """
        Busca as movimentações de cada tipo de ativo e as consolida em um
        dataframe único. Caso não haja, retorna um dataframe vazio
        """
        import ativos.models as am

        object_type = ContentType.objects.get_for_model(am.Acao)
        carteira = self.juntar_movimentacoes_ativo(data_referencia, object_type)

        tipo_objeto = ContentType.objects.get_for_model(am.Renda_Fixa)
        carteira = carteira.append(self.juntar_movimentacoes_ativo(data_referencia, tipo_objeto))

        tipo_objeto = ContentType.objects.get_for_model(am.Caixa)
        carteira = carteira.append(self.juntar_movimentacoes_ativo(data_referencia, tipo_objeto))

        tipo_objeto = ContentType.objects.get_for_model(am.Fundo_Local)
        carteira = carteira.append(self.juntar_movimentacoes_ativo(data_referencia, tipo_objeto))

        tipo_objeto = ContentType.objects.get_for_model(am.Fundo_Offshore)
        carteira = carteira.append(self.juntar_movimentacoes_ativo(data_referencia, tipo_objeto))

        return carteira

    def juntar_movimentacoes_ativo(self, data_referencia, object_type):
        """
        Busca todas as movimentações de um determinado tipo de ativo, com data
        igual à data de movimentação.
        """
        mov = Movimentacao.objects.filter(data=data_referencia, fundo=self,\
            tipo_movimentacao=object_type)

        if mov:
            # Transformando o resultado em dataframe
            df_mov = pd.DataFrame(list(mov.values('id', 'data', 'fundo', 'valor', 'tipo_id', 'tipo_movimentacao_id')))
            # buscando a custodia dos ativos movimentados
            import boletagem.models as bm
            import ativos.models as am
            import mercado.models as mm
            dicionario_boleta_custodia = []
            for m in mov:
                if type(m.content_object) != bm.BoletaProvisao:
                    if type(m.content_object) == bm.BoletaAcao or \
                        type(m.content_object) == bm.BoletaRendaFixaLocal or \
                        type(m.content_object) == bm.BoletaRendaFixaOffshore:
                        dicionario_boleta_custodia.append({'id':m.id, \
                            'custodia_id':m.content_object.custodia_id, \
                            'corretora_id':m.content_object.corretora.id,\
                            'descricao':m.__str__()})
                    elif type(m.content_object) == mm.Provento:
                        # No caso de provento, como a boleta de provisao possuirá
                        # a mesma referência da movimentação, podemos buscar pela
                        # boleta de provisão que aponta para o provento.
                        provisao = bm.BoletaProvisao.objects.get(content_type=m.content_type, \
                            object_id=m.object_id)
                        dicionario_boleta_custodia.append({'id':m.id, \
                            'custodia_id':provisao.caixa_alvo.custodia.id, \
                            'corretora_id':provisao.caixa_alvo.corretora.id,\
                            'descricao':m.__str__()})
                    else:
                        dicionario_boleta_custodia.append({'id':m.id, \
                        'custodia_id':m.content_object.custodia_id, \
                        'corretora_id':m.content_object.caixa_alvo.corretora.id, \
                        'descricao':m.__str__()})
                    # dicionario_boleta_custodia.append({'id':m.id, 'custodia_id':m.content_object.custodia_id, 'descricao':m.__str__()})
                else:
                    dicionario_boleta_custodia.append({'id':m.id, \
                    'custodia_id':m.content_object.caixa_alvo.custodia.id, \
                    'corretora_id':m.content_object.caixa_alvo.corretora.id, \
                    'descricao':m.content_object.descricao})
            # Dataframe de boletas com custódia
            # Possui id_quantidade(id), id_custodia
            custodia = pd.DataFrame(dicionario_boleta_custodia)
            # Possui id_ativo (id)
            ativos = pd.DataFrame(list(am.Ativo.objects.all().values('id', 'nome', 'moeda')))

            df_mov = df_mov.merge(custodia, right_on='id', left_on='id')
            """
            Este último join pode vir a ser removido futuramente.
            """
            df_mov = df_mov.merge(ativos, right_on='id', \
                left_on='tipo_id').drop(['id_y'], axis=1)

            df_mov['data'] = data_referencia
            return df_mov

        else:
            return pd.DataFrame()

    def criar_vertices(self, data_referencia):
        """ Date -> None
        Recebe uma data de referência, junta as quantidades e movimentações
        de ativos e cria os vértices da carteira baseado nas quantidades e
        movimentações, retorna uma lista de id de todos os vértices criados
        """
        import ativos.models as am
        import mercado.models as mm
        import configuracao.models as cm
        import math

        carteira_qtd = self.juntar_quantidades(data_referencia)
        carteira_mov = self.juntar_movimentacoes(data_referencia)
        df_cambios = self.buscar_cambios(data_referencia)

        lista_qtds = pd.DataFrame()
        if carteira_qtd.empty == False:
            # Antes de criar os vértices, precisamos consolidar as quantidades e
            # ver quais ativos já estão com posição zerada, consolidando o dataframe
            # por tipo_id (id do ativo) e custodia_id(id da custódia do ativo.)

            carteira_qtd_completa = (carteira_qtd.groupby(['nome', 'fundo', \
                'data', 'custodia_id', 'corretora_id', 'tipo_id', 'id_x',\
                'tipo_quantidade_id', 'moeda'])['qtd'].sum().to_frame())

            carteira_qtd_consolidada = (carteira_qtd.groupby(['nome', 'fundo', \
                'data', 'custodia_id', 'corretora_id', 'tipo_id', \
                'tipo_quantidade_id', 'moeda'])['qtd'].sum().to_frame())
            carteira_qtd_completa.reset_index(inplace=True)

            lista_qtds = carteira_qtd_consolidada[carteira_qtd_consolidada['qtd'] != 0].merge(carteira_qtd_completa, how='inner', \
                left_on=['nome', 'fundo', 'data', 'custodia_id', 'corretora_id', \
                'tipo_id', 'tipo_quantidade_id', 'moeda'], \
                right_on=['nome', 'fundo', 'data', 'custodia_id', 'corretora_id', \
                'tipo_id', 'tipo_quantidade_id', 'moeda'])[['id_x', 'nome', 'fundo', 'data', 'custodia_id', \
                    'corretora_id', 'tipo_id', 'qtd_x', 'tipo_quantidade_id', 'moeda']]

            lista_qtds.rename(columns={'id_x':'id_qtd', 'qtd_x':'qtd'}, inplace=True)
            lista_qtds.set_index(['nome', 'fundo', 'data', 'custodia_id', \
                'corretora_id', 'tipo_id', 'moeda'], inplace=True)

        lista_movs = pd.DataFrame()
        if carteira_mov.empty == False:
            carteira_mov_completa = (carteira_mov.groupby(['nome', 'fundo', \
                'data', 'custodia_id', 'corretora_id', 'tipo_id', 'id_x', \
                'tipo_movimentacao_id', 'moeda'])['valor'].sum().to_frame())

            carteira_mov_consolidada = (carteira_mov.groupby(['nome', 'fundo', \
                'data', 'custodia_id', 'corretora_id', 'tipo_id', \
                'tipo_movimentacao_id', 'moeda'])['valor'].sum().to_frame())

            carteira_mov_completa.reset_index(inplace=True)

            # Lista que encontra as posições que não possuem posição zerada.
            # Compara a carteira com as posições consolidadadas vs a carteira aberta
            # exaustivamente.
            lista_movs = carteira_mov_consolidada[carteira_mov_consolidada['valor'] != 0].merge(carteira_mov_completa, how='inner', \
                left_on=['nome', 'fundo', 'data', 'custodia_id', 'corretora_id', \
                'tipo_id', 'moeda'], \
                right_on=['nome', 'fundo', 'data', 'custodia_id', 'corretora_id', \
                'tipo_id', 'moeda'])[['id_x', 'nome', 'fundo', 'data', 'custodia_id', \
                    'corretora_id', 'tipo_id', 'valor_x', 'tipo_movimentacao_id', 'moeda']]

            lista_movs.rename(columns={'id_x':'id_mov', 'valor_x':'mov'}, inplace=True)

            lista_movs.set_index(['nome', 'fundo', 'data', 'custodia_id', \
                'corretora_id', 'tipo_id', 'moeda'], inplace=True)

        # Juntando lista de qtd e mov
        lista_vertices = pd.DataFrame()
        if lista_movs.empty == False and lista_qtds.empty == False:
            lista_vertices = lista_movs.join(lista_qtds, how='outer')
        elif lista_movs.empty == True:
            lista_qtds['mov'] = decimal.Decimal('0')
            lista_qtds['id_mov'] = decimal.Decimal('0')
            lista_qtds['tipo_movimentacao_id'] = lista_qtds['tipo_quantidade_id']
            lista_vertices = lista_qtds.copy()
        elif lista_qtds.empty == True:
            lista_movs['qtd'] = decimal.Decimal('0')
            lista_movs['id_qtd'] = decimal.Decimal('0')
            lista_movs['tipo_quantidade_id'] = lista_movs['tipo_movimentacao_id']
            lista_vertices = lista_movs.copy()
        df_tipo_objeto = lista_vertices['tipo_movimentacao_id'].fillna(lista_vertices['tipo_quantidade_id']).to_frame()
        df_tipo_objeto.rename(columns={'tipo_movimentacao_id':'tipo_objeto_id'}, inplace=True)
        lista_vertices = lista_vertices.merge(df_tipo_objeto, how='inner', left_index=True, right_index=True).drop_duplicates()
        lista_vertices = lista_vertices.drop(['tipo_movimentacao_id','tipo_quantidade_id'], axis=1)
        lista_vertices.fillna(decimal.Decimal('0'), inplace=True)
        lista_vertices = lista_vertices.join(df_cambios, on='moeda')
        lista_vertices.fillna(decimal.Decimal('1'), inplace=True)
        lista_vertices.reset_index('moeda', inplace=True)
        lista_vertices = lista_vertices.drop(['moeda', 'moeda_destino'], axis=1)
        lista_vertices.rename(columns={'preco_fechamento':'cambio'}, inplace=True)

        index_list = lista_vertices.index.tolist()
        index_names = lista_vertices.index.names

        lista_vertice_id = list()

        # Set pega os objetos distintos do index_list para criar os vértices.
        # Desta forma, não há double counting de vértices
        for ativo in set(index_list):
            # Criando o vértice com os valores
            vertice = dict()
            index_values = lista_vertices.loc[ativo].index.tolist()[0]
            for i, valor in enumerate(index_values):
                vertice[index_names[i]] = valor
            ativo_vertice = am.Ativo.objects.get(id=vertice['tipo_id'])

            preco = mm.Preco.objects.filter(data_referencia__lte=vertice['data'].date(),\
                ativo=ativo_vertice).order_by('-data_referencia').first()
            preco_fechamento = 0

            if preco == None:
                preco_fechamento = decimal.Decimal(1)
            else:
                preco_fechamento = decimal.Decimal(preco.preco_fechamento).quantize(decimal.Decimal('1.000000'))

            fundo = Fundo.objects.get(id=vertice['fundo'])

            corretora = Corretora.objects.get(id=vertice['corretora_id'])

            custodia = Custodiante.objects.get(id=vertice['custodia_id'])

            quantidade = decimal.Decimal(lista_vertices.loc[ativo]['qtd'].values[0])

            movimentacao = decimal.Decimal(lista_vertices.loc[ativo]['mov'].values[0])

            content_type = ContentType.objects.get_for_id(lista_vertices.loc[ativo]['tipo_objeto_id'].values[0])

            cambio = lista_vertices.loc[ativo]['cambio'].values[0]

            novo_vertice = Vertice(
                fundo=fundo,
                custodia=custodia,
                corretora=corretora,
                quantidade=quantidade,
                movimentacao=movimentacao*cambio,
                valor=preco_fechamento*quantidade*cambio,
                data=vertice['data'].date(),
                content_type=content_type,
                object_id=vertice['tipo_id'],
                preco=preco_fechamento,
                cambio=cambio
            )
            novo_vertice.save()
            vertice_id = novo_vertice.id

            # Criando os itens de casamento entre quantidade e vértice
            # Tuplas = (quantidade_id, vertice_id)

            for id in lista_vertices.loc[ativo]['id_qtd'].drop_duplicates():
                if id != 0:
                    cas_qtd_vert = CasamentoVerticeQuantidade(
                        vertice=novo_vertice,
                        quantidade=Quantidade.objects.get(id=id)
                    )
                    cas_qtd_vert.save()

            for id in lista_vertices.loc[ativo]['id_mov'].drop_duplicates():
                if id != 0:
                    cas_mov_vert = CasamentoVerticeMovimentacao(
                        vertice=novo_vertice,
                        movimentacao=Movimentacao.objects.get(id=id)
                    )
                    cas_mov_vert.save()

    def buscar_cambios(self, data_referencia):
        """ date -> DataFrame
        Busca os valores dos cambios na data de referencia. Recebe uma data
        de referência e devolve um dataframe com os câmbios, e os códigos das
        moedas de origem e destino do câmbio.
        """
        import configuracao.models as cm
        import mercado.models as mm
        import ativos.models as am

        # Buscando os câmbios do dia
        configuracao = cm.ConfigCambio.objects.get(fundo=self)

        cambios_padrao = configuracao.cambio.all()
        # Preço de fechamento dos cambios padrões na data referencia
        preco_cambios = mm.Preco.objects.filter(ativo__in=cambios_padrao, \
            data_referencia=data_referencia).exclude(preco_fechamento=None)
        df_precos = pd.DataFrame(list(preco_cambios.values('ativo',\
            'preco_fechamento')))
        df_precos.set_index('ativo', inplace=True)
        # Pegando todos os ativos do tipo cambio
        cambios = am.Cambio.objects.all()
        df_cambios = pd.DataFrame(list(cambios.values('id', 'moeda_origem',\
            'moeda_destino')))
        df_cambios.set_index('id', inplace=True)
        df_preco_cambios = df_cambios.join(df_precos, how='inner')
        df_preco_cambios.set_index('moeda_origem', inplace=True)
        return df_preco_cambios

    def cambio_do_dia(self, data_referencia, moeda):
        """ date, Moeda -> decimal
        Recebe uma data de referencia e uma moeda. Retorna o valor do câmbio
        entre a moeda recebida e a moeda do fundo na data de referencia
        """
        import configuracao.models as cm
        import ativos.models as am
        import mercado.models as mm

        configuracao = cm.ConfigCambio.objects.filter(fundo=self)
        if configuracao.count() == 0:
            return decimal.Decimal(1)
        else:
            configuracao = configuracao[0]
        cambios_padrao = configuracao.cambio.all()
        cambio_usado = None
        for cambio in cambios_padrao:
            if cambio.moeda_origem == moeda:
                cambio_usado = cambio

        if cambio_usado == None:
            return decimal.Decimal(1)
        else:
            valor_cambio = mm.Preco.objects.filter(ativo=cambio_usado, \
                data_referencia=data_referencia).exclude(preco_fechamento=None)[0]

            if valor_cambio==None:
                raise ValueError("Câmbio indisponível: " + cambio_usado.nome + " " + data_referencia.strftime('%d/%m/%Y'))
            return decimal.Decimal(valor_cambio.preco_fechamento).quantize(decimal.Decimal('1.000000'))

    def consolidar_vertices(self, data_referencia):
        """ datetime.Date -> pd.DataFrame
        Junta todos os vértices criados.
        """
        import boletagem.models as bm
        import ativos.models as am
        #
        boletas = pd.DataFrame(list(bm.BoletaCPR.objects.all().values('id', 'descricao')))
        # Buscando os vértices criados.
        v = Vertice.objects.filter(data=data_referencia).values('object_id', \
            'fundo', 'data', 'valor', 'movimentacao', 'content_type_id', \
            'quantidade', 'preco', 'cambio')

        ativos = pd.DataFrame(list(am.Ativo.objects.all().values('id', 'nome')))
        content = pd.DataFrame(list(ContentType.objects.all().values('id', 'app_label', 'model')))
        vertices = pd.DataFrame(list(v))
        v_ativos = vertices.merge(ativos, left_on='object_id', right_on='id').drop(['object_id'], axis=1)
        v_cpr = vertices.merge(boletas, left_on='object_id', right_on='id').drop(['object_id'], axis=1)

        import pdb
        pdb.set_trace()

        # print('LISTA DE VÉRTICES:')
        # vertices = vertices.merge(boletas, left_on='object_id', right_on='id').drop(['id'], axis=1)
        return vertices

    def calcular_cota(self, data_referencia):
        """
        Dada uma data, busca os vértices relevantes para a data, calcula o PL
        e a cota do dia.
        """
        vertices = self.consolidar_vertices(data_referencia)
        carteira = Carteira()
        carteira.inicializar(vertices)
        carteira.save()

    def reprocessar_cota(self, data_referencia):
        """
        Na ordem do fechamento, atualizar as boletas de CPR, provisão,
        Quantidades, Movimentações e Vértices com data igual à data de
        referencia.

        REPROCESSAMENTO ALTERNATIVO: DELETAR TUDO E REFAZER:

        Dada uma data de referência, para reprocessar a cota, é necessário
        fazer o processo inverso do fechamento.
        Na ordem:
            1) Deletar a Carteira.
            2) Deletar os vértices com data igual à data de referência.
            3) A partir das boletas de provisão:
                1) Buscar as quantidades criadas e deletá-las
                2) Buscar as movimentações criadas e deleta-las
            4) A partir das boletas de CPR:
                1) (Os vértices criados já foram deletados no passo anterior)
            5) A partir das boletas de passivo:
                Em caso de aporte:
                    1) Apagar o certificado de passivo criado e ligado à boleta
                Em caso de resgate: A partir da diferença do número de cotas
                da carteira do dia anterior ao resgate e posterior ao resgtate,
                conseguimos o número de cotas resgatadas. Desfaz o resgate,
                reatribuindo cotas aos certificados ligados à boleta de passivo,
                partindo do certificado mais recente até o mais antigo.
                Em caso de resgate total: A partir da quantidade de cotas da
                carteira anterior, conseguimos o número de cotas resgatadas.
                Então fazemos como um resgate normal.
                    2) Apagar as boletas de provisão e CPR criadas.
            6) Apaga boletas de passivo que possuam content_object ligadas a
            ela, pois são boletas frutos do fechamento de outras boletas.
            7)
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
    Descreve a carteira de um fundo ao final do dia numa determinada data. A
    partir da carteira, podemos gerar a lâmina do fundo.
    """
    fundo = models.ForeignKey('Fundo', on_delete=models.PROTECT)
    vertices = models.ManyToManyField('Vertice')
    data = models.DateField()
    cota = models.DecimalField(max_digits=17, decimal_places=8)
    pl = models.DecimalField(max_digits=15, decimal_places=2)
    movimentacao = models.DecimalField(max_digits=13, decimal_places=2)

    class Meta:
        ordering = ['fundo']
        verbose_name_plural = 'Carteiras'

    def inicializar(self, df_vertices):
        """
        Recebe os vértices de um fundo, e cria a carteira. O dataFrame deve
        possuir colunas correspondentes ao id do fundo (nome 'fundo'), data de
        referencia dos vértices ('data'), valor financeiro do vértice ('valor') e
        movimentação ('movimentacao')
        """

        consolidado = df_vertices.groupby(['fundo', 'data'])[['valor', \
            'movimentacao']].sum()
        consolidado.reset_index(inplace=True)
        self.data = consolidado['data'][0]
        self.fundo = Fundo.objects.get(id=consolidado['fundo'][0])
        self.pl = decimal.Decimal(consolidado['valor'][0]).quantize(decimal.Decimal('1.00'))
        self.movimentacao = decimal.Decimal(consolidado['movimentacao'][0]).quantize(decimal.Decimal('1.00'))
        # Buscar todos os certificados para ver quantas cotas o fundo possui
        total_cotas = CertificadoPassivo.total_cotas_aplicadas(fundo=self.fundo,\
            data_referencia=self.data)
        self.cota = decimal.Decimal(self.pl/total_cotas).quantize(decimal.Decimal('1.00000000'))

        self.save()
        vertices = Vertice.objects.filter(fundo=self.fundo, data=self.data)
        for vertice in vertices:
            self.vertices.add(vertice)

        import pdb
        pdb.set_trace()

        self.save()

    def pl_nao_gerido(self, data_referencia):
        """
        Recebe uma data de referência, e retorna o PL do fundo descontando ativos
        que são geridos.
        """
        import ativos.models as am
        pl_gerido = 0
        for v in self.vertices.all():
            if type(v.content_object) == am.Fundo_Local:
                if v.content_object.gerido() == True:
                    pl_gerido += v.valor
        return self.pl - pl_gerido

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
    corretora = models.ForeignKey('Corretora', on_delete=models.PROTECT, \
        blank=True, null=True)
    # Quantidade do ativo.
    quantidade = models.DecimalField(decimal_places=6, max_digits=20)
    # Valor financeiro do ativo na moeda do fundo.
    valor = models.DecimalField(decimal_places=2, max_digits=20)
    # Preço do ativo.
    preco = models.DecimalField(decimal_places=6, max_digits=20)
    # Data relativa ao preço utilizada
    data_preco = models.DateField(default=datetime.date.today)
    # Valor da movimentação do ativo/CPR.
    movimentacao = models.DecimalField(decimal_places=6, max_digits=20, default=decimal.Decimal(0))
    data = models.DateField()
    # Caso a moeda original do ativo seja diferente da do fundo, indica o valor usado.
    cambio = models.DecimalField(decimal_places=6, max_digits=12, default=decimal.Decimal('1'))

    # O content_type pode ser tanto um ativo quanto uma boleta de CPR
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT,
        related_name='relacao_ativo')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['fundo']
        verbose_name_plural = 'Vértices'

    def __str__(self):
        from boletagem import models as bm

        objeto = ''
        if type(self.content_object) == bm.BoletaCPR:
            objeto = self.content_object.descricao
        else:
            objeto = self.content_object.nome

        custodia_texto = ''
        if self.custodia != None:
            custodia_texto = self.custodia.nome

        corretora_texto = ''
        if self.corretora != None:
            corretora_texto = self.corretora.nome

        d = {
            "fundo":self.fundo.nome,
            "custodia":custodia_texto,
            "corretora":corretora_texto,
            "quantidade":str(self.quantidade),
            "valor":str(self.valor),
            "preco":str(self.preco),
            "movimentacao":str(self.movimentacao),
            "data":self.data,
            "cambio":str(self.cambio),
            "objeto":objeto
        }
        return str(d)

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
        return 'Ativo: %s' % (self.content_object.__str__()) + \
            '\nQuantidade: %s' % (self.qtd)

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

    def __str__(self):
        return self.nome

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
    valor_cota = models.DecimalField(max_digits=14, decimal_places=6)
    # Quantidade de cotas desta série que ainda estão aplicadas.
    # Conforme o cotista realiza resgates do fundo, cotas de certificados mais
    # antigos são resgatadas, aumentando o valor da cota média.
    cotas_aplicadas = models.DecimalField(max_digits=15, decimal_places=7)
    # Data da aplicação
    data = models.DateField()
    # Fundo em que o cotista está aplicado.
    fundo = models.ForeignKey('fundo.fundo', on_delete=models.PROTECT)

    @staticmethod
    def total_cotas_aplicadas(fundo, data_referencia):
        """ Fundo, date -> decimal
        Dado um fundo, e uma data, busca o total de cotas aplicadas no fundo
        """
        certificados = CertificadoPassivo.objects.filter(fundo=fundo, \
            data__lte=data_referencia)
        df_cert = pd.DataFrame(list(certificados.values('data', 'fundo', \
            'cotas_aplicadas')))
        return df_cert.groupby(['data','fundo'])['cotas_aplicadas'].sum()[0]
