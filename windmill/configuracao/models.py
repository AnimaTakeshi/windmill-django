from django.db import models
import ativos.models as am

# Create your models here.
class ConfigCambio(models.Model):
    """
    Classe que representa o câmbio padrão para um fundo.
    """

    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.CASCADE)
    # um mesmo fundo pode possuir vários câmbios padrão.
    # TODO: Ao adicionar um novo câmbio, certificar-se de que não há um
    # configurado para as mesmas moedas.
    cambio = models.ManyToManyField('ativos.Cambio')

class ConfigZeragem(models.Model):
    """
    Classe que representa os caixas e a zeragem usada pelos caixas de um fundo.
    """

    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.CASCADE)
    caixa = models.ForeignKey(
        'ativos.Caixa',
        on_delete=models.PROTECT,
        related_name='config_zeragem_caixa')
    indice_zeragem = models.ForeignKey('ativos.Ativo',
        on_delete=models.PROTECT,
        related_name='config_zeragem_indice_zeragem')
