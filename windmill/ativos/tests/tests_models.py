import datetime
from django.test import TestCase
import django.contrib.contenttypes
import pytest
from model_mommy import mommy
import ativos.models as am

class FundoLocalUnitTest(TestCase):
    """
    Classe de unit tests de ativos tipo fundo local
    """
    def setUp(self):
        self.gestora_anima = mommy.make('fundo.Gestora',
            nome='SPN',
            anima=True
        )
        self.gestora_qualquer = mommy.make('fundo.Gestora',
            anima=False
        )
        self.fundo_gerido = mommy.make('fundo.Fundo',
            nome='Veredas',
            gestora=self.gestora_anima,
            data_de_inicio=datetime.date(year=2014, month=10, day=27),
            categoria="Fundo de Ações"
        )
        self.fundo_qualquer = mommy.make('fundo.Fundo',
            gestora=self.gestora_qualquer
        )
        self.ativo_fundo_gerido = mommy.make('ativos.Fundo_Local',
            gestao=self.fundo_gerido
        )
        self.ativo_fundo_qualquer = mommy.make('ativos.Fundo_Local',
            gestao=self.fundo_qualquer
        )


    def test_checa_gerido(self):
        """
        Checa se o fundo se identifica como gerido ou não, dependendo
        da gestora.
        """
        self.assertTrue(self.ativo_fundo_gerido.gerido())
        self.assertFalse(self.ativo_fundo_qualquer.gerido())
