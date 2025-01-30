from unittest import TestCase

from main import ObserverManagerFactory, view_to_mediator_mapping


class test_Main(TestCase):
    def test_factory_view_observer(self):
        from src.views.consoleview import ConsoleView
        from src.classes.zustandsbeobachter import ObserverManager

        objekt = ObserverManagerFactory.factory_from_liste([], view_to_mediator_mapping)
        self.assertIsInstance(objekt, ObserverManager)
        self.assertFalse(objekt.registrierte_view_klassen)
        self.assertFalse(objekt.beobachter)

        objekt = ObserverManagerFactory.factory_from_liste([ConsoleView()], view_to_mediator_mapping)
        self.assertIsInstance(objekt, ObserverManager)
        self.assertTrue(objekt.registrierte_view_klassen)
        self.assertIsNotNone(objekt.registrierte_view_klassen[ConsoleView])
        self.assertEqual('zustand_to_consoleview_data',
                         objekt.registrierte_view_klassen[ConsoleView][
                             ObserverManager().views_updaten.__func__.__name__].__func__.__name__)
        self.assertIsInstance(objekt.beobachter[0], ConsoleView)

        objekt = ObserverManagerFactory.factory_from_liste([ConsoleView(), ConsoleView()], view_to_mediator_mapping)
        self.assertIsInstance(objekt, ObserverManager)
        self.assertTrue(objekt.registrierte_view_klassen)
        self.assertEqual(1, len(list(objekt.registrierte_view_klassen.keys())))
        self.assertEqual(2, len(objekt.beobachter))
