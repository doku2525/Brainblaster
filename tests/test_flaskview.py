from unittest import TestCase
from unittest.mock import MagicMock

from src.views.flaskview import FlaskView, request_to_route
from src.classes.eventmanager import EventManager


class test_FlaskView(TestCase):

    def setUp(self):
        self.app = FlaskView(EventManager())
        self.app.cmd = MagicMock()
        self.app.data = {'liste': [1, 2, 3, 4],
                         'aktuelle_uhrzeit': '2024-07-01 18:00:00.000000',
                         'aktueller_index': 0,
                         'zustand': 'ZustandStart'}
        self.client = self.app.app.test_client()
        self.app_lernuhr = FlaskView(EventManager())
        self.app_lernuhr.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                                 'neue_uhrzeit': '2024-12-24 18:00:00.000000',
                                 'neue_uhr': {'kalkulations_zeit': '2024-12-03 19:32:33.000000',
                                              'start_zeit': '2024-07-10 09:07:24.987000',
                                              'tempo': 1.0,
                                              'pause': 0,
                                              'modus': 'LAEUFT'}}
        self.client_lernuhr = self.app_lernuhr.app.test_client()
        self.app_boxinfo = FlaskView(EventManager())
        self.app_boxinfo.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                                 'info': {'a1': {'pruefen': {'insgesamt': 0, 'aktuell': 0},
                                                 'lernen': {'insgesamt': 0, 'aktuell': 0},
                                                 'neu': {'insgesamt': 0, 'aktuell': 0}},
                                          'a2': {'pruefen': {'insgesamt': 0, 'aktuell': 0},
                                                 'lernen': {'insgesamt': 0, 'aktuell': 0},
                                                 'neu': {'insgesamt': 0, 'aktuell': 0}}},
                                 'aktuelle_frageeinheit': 'a1',
                                 'box_titel': 'Box1',
                                 'zustand': 'ZustandBoxinfo'}
        self.client_boxinfo = self.app_boxinfo.app.test_client()
        self.app_testen = FlaskView(EventManager())
        self.app_testen.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                                'frage': 'Frage',
                                'antwort': 'Antwort',
                                'formatierung': 'Chinesisch',
                                'zustand': 'ZustandVokabelPruefen'}
        self.client_testen = self.app_testen.app.test_client()
        self.app_pruefen = FlaskView(EventManager())
        self.app_pruefen.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                                 'frage': 'Frage',
                                 'antwort': 'Antwort',
                                 'formatierung': 'Chinesisch',
                                 'zustand': 'ZustandVokabelPruefen'}
        self.client_pruefen = self.app_pruefen.app.test_client()
        self.app_lernen = FlaskView(EventManager())
        self.app_lernen.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                                'frage': 'Frage',
                                'antwort': 'Antwort',
                                'formatierung': 'Chinesisch',
                                'zustand': 'ZustandVokabelLernen'}
        self.client_lernen = self.app_lernen.app.test_client()
        self.app_neue = FlaskView(EventManager())
        self.app_neue.data = {'aktuelle_uhrzeit': '2024-12-01 18:00:00.000000',
                              'frage': 'Frage',
                              'antwort': 'Antwort',
                              'formatierung': 'Chinesisch',
                              'zustand': 'ZustandVokabelNeue'}
        self.client_neue = self.app_neue.app.test_client()

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
        self.assertEqual('<!--index.html-->', response.text.split("\n")[0])

    def test_route_index(self):
        response = self.client.get('/index')
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!--index.html-->', response.text.split("\n")[0])

    def test_route_editor_lernuhr(self):
        response = self.client_lernuhr.get('/editor_lernuhr')
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!--editor_lernuhr.html-->', response.text.split("\n")[0])

    def test_route_boxinfo(self):
        response = self.client_boxinfo.get('/boxinfo')
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!--boxinfo.html-->', response.text.split("\n")[0])

    def test_route_vokabeln_testen(self):
        response = self.client_testen.get('/karten_testen')
        self.assertEqual(200, response.status_code)
        self.assertEqual('<!--karten_testen.html-->', response.text.split("\n")[0])

    def test_route_vokabeln_pruefen(self):
        response = self.client_pruefen.get('/karten_pruefen')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/karten_testen', response.headers['Location'])

    def test_route_vokabeln_lernen(self):
        response = self.client_pruefen.get('/karten_lernen')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/karten_testen', response.headers['Location'])

    def test_route_vokabeln_neue(self):
        response = self.client_pruefen.get('/karten_neue')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/karten_testen', response.headers['Location'])

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

    def test_route_get_aktuellen_zustand(self):
        response = self.client.get('/get_aktuellen_zustand')
        self.assertEqual(200, response.status_code)
        self.assertIn("ZustandStart",
                      response.data.decode('utf-8'),
                      "Teste mit assertIn, da data noch voller \n und Stringzeichen.")
        response = self.client_boxinfo.get('/get_aktuellen_zustand')
        self.assertEqual(200, response.status_code)
        self.assertIn("ZustandBoxinfo",
                      response.data.decode('utf-8'),
                      "Teste mit assertIn, da data noch voller \n und Stringzeichen.")

    def test_route_get_aktuelle_frage_und_antwort(self):
        response = self.client.get('/get_aktuelle_frage_und_antwort')
        self.assertEqual(200, response.status_code)
        expected = b'{"antwort":"","frage":""}\n'
        self.assertIn(expected, response.data)
        response = self.client_pruefen.get('/get_aktuelle_frage_und_antwort')
        self.assertEqual(200, response.status_code)
        expected = b'{"antwort":"Antwort","frage":"Frage"}\n'
        self.assertIn(expected, response.data)

    def test_route_get_aktuelle_und_neue_uhrzeit(self):
        response = self.client.get('/get_aktuelle_und_neue_uhrzeit')
        self.assertEqual(500, response.status_code)
        response = self.client_lernuhr.get('/get_aktuelle_und_neue_uhrzeit')
        self.assertEqual(200, response.status_code)
        expected = b'{"aktuelle_uhrzeit":"2024-12-01 18:00:00","neue_uhr":{"kalkulations_zeit":"2024-12-03 19:32:33.000000","modus":"LAEUFT","pause":0,"start_zeit":"2024-07-10 09:07:24.987000","tempo":1.0},"neue_uhrzeit":"2024-12-24 18:00:00"}\n'
        self.assertIn(expected, response.data)

    def test_lade_neuen_zustand(self):
        response = self.client.get('/lade_neuen_zustand')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/index', response.headers['Location'])
        response = self.client_boxinfo.get('/lade_neuen_zustand')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/boxinfo', response.headers['Location'])
        response = self.client_pruefen.get('/lade_neuen_zustand')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/karten_pruefen', response.headers['Location'])
        response = self.client_lernen.get('/lade_neuen_zustand')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/karten_lernen', response.headers['Location'])
        response = self.client_neue.get('/lade_neuen_zustand')
        self.assertEqual(302, response.status_code)
        self.assertEqual('/karten_neue', response.headers['Location'])
