from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.admin.models import ADDITION, CHANGE, DELETION
from django.contrib.admin.options import (
    HORIZONTAL, VERTICAL, ModelAdmin, TabularInLine,
    get_content_type_for_model,
)
from django.contrib.admin.sites import AdminSite
from django.db import models


# Create your tests here.
class ModelAdminTests(TestCase):

    def test_url_acoes_resolves(self):
        response = self.client.get('/ativos/acoes/')
        self.assertEqual(response.status_code, 200)

    def test_cadastro_url_returns_correct_html(self):
        response = self.client.get('/ativos/acoes/')
        html = response.content.decode('utf8')
        self.assertIn('<h1>Cadastro de ações</h1>', html)

    def test_url_lista_acao_resolves(self):
        response= = self.client.get('/ativos/acoes/lista')
        self.assertEqual(response.status_code, 200)
