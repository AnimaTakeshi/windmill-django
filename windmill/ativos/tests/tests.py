from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
import ativos.views
from ativos.views import ativos_home
from ativos.views import acoes

# Create your tests here.
class AtivosPageTest(TestCase):

    # def test_root_ativos_url_resolves(self):
    #     """
    #     Testing if the URL routing to ativos app is working
    #     correctly.
    #     Expected URL = root/ativos/
    #     """
    #     found = resolve('/ativos/')
    #     self.assertEqual(found.func, ativos_home)

    def test_url_acoes_resolves(self):
        response = self.client.get('/ativos/acoes/')
        self.assertEqual(response.status_code, 200)

    def test_cadastro_url_returns_correct_html(self):
        response = self.client.get('/ativos/acoes/')
        html = response.content.decode('utf8')
        self.assertIn('<h1>Cadastro de ativos</h1>', html)
