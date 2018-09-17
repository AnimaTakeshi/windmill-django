from django.db import models
import datetime

# Create your models here.


class Boleta_Acao(models.Model):

    acao = models.ForeignKey("ativos.Acao", on_delete=models.PROTECT)
    data_operacao = models.DateField(default=datetime.date.today, null=False)
    data_liquidacao = models.DateField()
    corretora = models.ForeignKey("fundo.Corretora", null=False, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Boletas de operação de ações"

    def __str__(self):
        return "Operação de '%s' executada em '%s'." % (self.acao, self.data_operacao)
