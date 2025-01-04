from unittest import TestCase
from unittest.mock import patch
from src.classes.zustandsbeobachter import ObserverManager, Beobachter
from src.zustaende.zustandstart import ZustandStart


class MockView(Beobachter):
    def __init__(self):
        self.received_data = ''
        self.rendered = False

    def update(self, data):
        self.received_data = data

    def render(self):
        self.rendered = True

    @staticmethod
    def konverter(x, y):
        return {x: x * x, y: y * y}


class TestObserverManager(TestCase):

    def setUp(self):
        self.observer_manager = ObserverManager()
        self.mock_view = MockView()

    def test_registriere_mapping(self):
        result = self.observer_manager.registriere_mapping(MockView(),
                                                           MockView.konverter,
                                                           self.observer_manager.views_updaten)

        self.assertIn(MockView, result.registrierte_view_klassen.keys())
        self.assertIn(self.observer_manager.views_updaten.__func__.__name__,
                      result.registrierte_view_klassen[MockView].keys())
        self.assertEqual(
            result.registrierte_view_klassen[MockView][self.observer_manager.views_updaten.__func__.__name__],
            MockView.konverter)

    def test_view_anmelden(self):
        result = self.observer_manager.view_anmelden(self.mock_view)
        self.assertIn(self.mock_view, result.beobachter)

    def test_view_abmelden(self):
        self.observer_manager = self.observer_manager.view_anmelden(self.mock_view)
        result = self.observer_manager.view_abmelden(self.mock_view)
        self.assertNotIn(self.mock_view, result.beobachter)

    def test_suche_cmd(self):
        from typing import Callable

        objekt = self.observer_manager.registriere_mapping(self.mock_view,
                                                           MockView.konverter,
                                                           self.observer_manager.views_updaten)
        result = objekt.suche_cmd(self.mock_view, self.observer_manager.views_updaten, lambda: 1)
        self.assertEqual(MockView.konverter, result)
        self.assertIsInstance(result, Callable)
        self.assertEqual({1: 1, 2: 4}, result(1, 2))

        # Nicht vorhandene Funktion
        result = objekt.suche_cmd(self.mock_view, self.test_suche_cmd, lambda: 1)
        self.assertEqual(1, result())
        self.assertIsInstance(result, Callable)

        # Nicht Funktion ohne Attrib '__func__'
        result = objekt.suche_cmd(self.mock_view, lambda: None, lambda: 1)
        self.assertEqual(1, result())
        self.assertIsInstance(result, Callable)

        class MockViewZwei(Beobachter):
            pass

        # Nicht vorhandenes View-Objekt
        result = objekt.suche_cmd(MockViewZwei(), self.observer_manager.views_updaten, lambda: 1)
        self.assertEqual(1, result())
        self.assertIsInstance(result, Callable)

    def test_views_updaten(self):
        # Arrange
        self.observer_manager = self.observer_manager.view_anmelden(self.mock_view)
        zustand = ZustandStart()  # Ersetze durch deine tatsächliche Zustand-Klasse
        self.observer_manager.views_updaten(zustand, 100)
        self.assertEqual(self.mock_view.received_data, {})
        self.observer_manager.views_updaten(zustand, 100, lambda x, y: y)
        self.assertEqual(self.mock_view.received_data, 100)

    def test_views_updaten_zwei(self):
        from typing import cast
        from src.zustaende.zustand import Zustand

        objekt = self.observer_manager.registriere_mapping(self.mock_view,
                                                           MockView.konverter,
                                                           self.observer_manager.views_updaten)
        objekt.views_updaten(cast(Zustand, 1), 2)
        self.assertEqual({1: 1, 2: 4}, self.mock_view.received_data)

    def test_views_rendern(self):
        self.observer_manager = self.observer_manager.view_anmelden(self.mock_view)
        self.observer_manager.views_rendern()
        self.assertTrue(self.mock_view.rendered)

    # TODO Weitere Tests:
    # - Testen von Fehlern (z.B. wenn ein Beobachter nicht gefunden wird)
    # - Testen von komplexeren Szenarien mit mehreren Beobachtern und verschiedenen Funktionen
    # - Testen der `_suche_cmd`-Methode separat
