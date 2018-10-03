import requests
from requests.auth import HTTPBasicAuth
from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import django.contrib.contenttypes
import pytest
import ativos.views
from ativos.views import ativos_home
from ativos.views import acoes

# Create your tests here.
class AbstractPageTest(TestCase):
    """
    Classe abstrata base das classes de teste de URL. Todas elas precisam de
    acesso administrador
    """
    class Meta:
        abstract = True

    def setUp(self):
        self.admin_user = User.objects.create_superuser('ricardo',
            'r@g.com', 'senha')

class AuthenticationTest(AbstractPageTest):


    def test_authenticated(self):
        """
        Testa se o backend autentica o usuário criado no setUp
        """
        user = authenticate(username='ricardo', password='senha')
        self.assertIsNotNone(user)

    def test_login(admin_client):
        """
        Testa se conseguimos fazer o login com usuário criado no setup
        """
        pass

    # def test_url_acoes_resolves(self):
    #     response = self.client.get('/ativos/acoes/')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_cadastro_url_returns_correct_html(self):
    #     response = self.client.get('/ativos/acoes/')
    #     html = response.content.decode('utf8')
    #     self.assertIn('<h1>Cadastro de ações</h1>', html)
    #
    # def test_url_lista_acao_resolves(self):
    #     response = self.client.get('/ativos/acoes/lista')
    #     self.assertEqual(response.status_code, 200)
