import datetime
import decimal
from model_mommy import mommy
import pytest
from django.test import TestCase
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
import boletagem.models as bm
import fundo.models as fm

class FundoUnitTests(TestCase):
    """
    Guarda os UnitTests do modelo Fundo
    """
    # Teste - fechar boletas de ação
    # Teste - fechar boletas de renda fixa local
    # Teste - fechar boletas de renda fixa Offshore
    # Teste - fechar boletas de fundo local
    # Teste - fechar boletas de fundo local com o fundo como ativo negociado
    # Teste - fechar boletas de fundo offshore
    # Teste - fechar boletas de fundo offshore com o fundo como ativo negociado
    # Teste - fechar boleas de passivo.
