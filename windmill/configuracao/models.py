from django.db import models
import ativos.models as am

# Create your models here.
class ConfigCambio(models.Model):
    """
    Classe que representa o câmbio padrão para um fundo.
    """
    class Meta:
        verbose_name = "Configuração de câmbio"
        verbose_name_plural = "Configurações de câmbio"

    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.CASCADE)
    # um mesmo fundo pode possuir vários câmbios padrão.
    # TODO: Ao adicionar um novo câmbio, certificar-se de que não há um
    # configurado para as mesmas moedas.
    cambio = models.ManyToManyField('ativos.Cambio')

    def __str__(self):
        nomes_cambios = ''
        for c in self.cambio.all():
            nomes_cambios += "\n\tCâmbio = " + c.nome

        return """
        fundo = {0},{1}
        """.format(self.fundo, nomes_cambios)

class ConfigZeragem(models.Model):
    """
    Classe que representa os caixas e a zeragem usada pelos caixas de um fundo.
    """

    class Meta:
        verbose_name = "Configuração de zeragem de caixas"
        verbose_name_plural = "Configurações de zeragem de caixas"

    fundo = models.ForeignKey('fundo.Fundo', on_delete=models.CASCADE)
    caixa = models.ForeignKey(
        'ativos.Caixa',
        on_delete=models.PROTECT,
        related_name='config_zeragem_caixa')
    indice_zeragem = models.ForeignKey('ativos.Ativo',
        on_delete=models.PROTECT,
        related_name='config_zeragem_indice_zeragem')
