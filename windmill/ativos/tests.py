from django.test import TestCase
from django.urls import resolve
from ativos.views import home_page

# Create your tests here.
class AtivosPageTest(TestCase):

    def test_root_url_resolves(self):
        found = resolve('/ativos/')
        self.assertEqual(found.func, home_page)
