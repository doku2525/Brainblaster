from unittest import TestCase
from unittest.mock import MagicMock

from src.views.flaskview import FlaskView, request_to_route


class test_FlaskView(TestCase):

    def setUp(self):
        self.app = FlaskView()
        self.app.cmd = MagicMock()
        self.app.data = {'liste': [1, 2, 3, 4], 'aktuelle_uhrzeit': '2024-07-01 18:00:00.000000', 'aktueller_index': 0}
        self.client = self.app.app.test_client()
        self.app_lernuhr = FlaskView()
        self.app_lernuhr.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                                 'neue_uhrzeit': '2024-12-24 18:00:00.000000'}
        self.client_lernuhr = self.app_lernuhr.app.test_client()

    def test_request_to_route(self):
        adressen = [
            ('http://127.0.0.1:5000/', 'index'),
            ('http://127.0.0.1:5000/index', 'index'),
            ('http://127.0.0.1:5000/irgendwas', 'irgendwas')]
        for adresse, erwartet in adressen:
            self.assertEqual(erwartet, request_to_route(adresse))

    def test_route_root(self):
        redirect_message = ('<!doctype html>\n' +
                            '<html lang=en>\n' +
                            '<title>Redirecting...</title>\n' +
                            '<h1>Redirecting...</h1>\n' +
                            '<p>You should be redirected automatically to the target URL: <a ' +
                            'href="/index">/index</a>. If not, click the link.\n')
        response = self.client.get('/')
        self.assertEqual(302, response.status_code)     # 302 = Wird ungeleitet
        self.assertEqual('/index', response.headers['Location'])
        self.assertEqual(redirect_message, response.text)
        response = self.client.get(response.headers['Location'])
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!-index.html->', response.text.split("\n")[0])

    def test_route_index(self):
        response = self.client.get('/index')
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!-index.html->', response.text.split("\n")[0])

    def test_route_editor_lernuhr(self):
        response = self.client_lernuhr.get('/editor_lernuhr')
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!-editor_lernuhr.html->', response.text.split("\n")[0])

    def test_route_get_aktuelle_uhrzeit(self):
        response = self.client.get('/get_aktuelle_uhrzeit')
        self.assertEqual(200, response.status_code)
        self.assertIn("2024-07-01 18:00:00",
                      response.data.decode('utf-8'),
                      "Teste mit assertIn, da data noch voller \n und Stringzeichen.")
        response = self.client_lernuhr.get('/get_aktuelle_uhrzeit')
        self.assertEqual(200, response.status_code)
        self.assertIn("2024-12-01 18:00:00",
                      response.data.decode('utf-8'),
                      "Teste mit assertIn, da data noch voller \n und Stringzeichen.")

    def test_route_get_aktuelle_und_neue_uhrzeit(self):
        response = self.client.get('/get_aktuelle_und_neue_uhrzeit')
        self.assertEqual(500, response.status_code)
        response = self.client_lernuhr.get('/get_aktuelle_und_neue_uhrzeit')
        self.assertEqual(200, response.status_code)
        expected = b'{"aktuelle_uhrzeit":"2024-12-01 18:00:00","neue_uhrzeit":"2024-12-24 18:00:00"}\n'
        self.assertIn(expected, response.data)
