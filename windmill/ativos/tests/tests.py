from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from ativos.views import ativos_home
from ativos.views import acoes

# Create your tests here.
class AtivosPageTest(TestCase):

    def test_root_ativos_url_resolves(self):
        """
        Testing if the URL routing to ativos app is working
        correctly.
        Expected URL = root/ativos/
        """
        found = resolve('/ativos/')
        self.assertEqual(found.func, ativos_home)

    def test_root_ativos_url_returns_correct_html(self):
        """
        Testing if the html returned is the correct one.
        """
        request = HttpRequest()
        response = ativos_home(request)
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>Cadastro de ativos</title>', html)
        self.assertTrue(html.endswith('</html>'))

    def test_url_acoes_resolves(self):
        found = resolve('/ativos/acoes/')
        self.assertEqual(found.func, acoes)
