from unittest import TestCase

from src.views.consoleview import ConsoleView


class test_ConsoleView(TestCase):

    def setUp(self):
        self.args = {
            'zustand': 'ZustandStart',
            'aktuelle_zeit': '1970-01-01 01:01:01',
            'daten': ' 0 : 1\n 1 : 2\n 2 : 3\nAktuelle Box: 1',
            'optionen': (' 0 ZustandStelleUhr : Zustand, zum Stellen der Uhr.\n'
                         ' 1 ZustandStelleUhr : Zustand, zum Stellen der Uhr.\n'
                         "'s' + Zahl\n"
                         "'k' + Zahl\n"
                         "'t' + Zahl\n"
                         "'z' + Zahl\n"
                         "'p' + Zahl\n"
                         "'r' + Zahl\n"
                         "'c' + Zahl\n"
                         )}

    def test_init(self):
        obj = ConsoleView()
        self.assertIsInstance(obj, ConsoleView)
        self.assertIsInstance(obj.data, dict)

    def test_update(self):
        obj = ConsoleView()
        self.assertIsInstance(obj.update({}), ConsoleView)
        self.assertEqual({1: 2}, obj.update({1: 2}).data)

    def test_render(self):
        obj = ConsoleView(self.args)
        self.assertEqual(4, len(obj.data.keys()))
        obj.render()

    def test_render_aktueller_zustand(self):
        obj = ConsoleView(self.args)
        expected = '\n Aktueller Zustand: ZustandStart'
        self.assertEqual(expected, obj.render_aktueller_zustand())

    def test_render_aktuelles_datum(self):
        obj = ConsoleView(self.args)
        expected = '\n Aktuelles Datum: 1970-01-01 01:01:01'
        self.assertEqual(expected, obj.render_aktuelles_datum())

    def test_render_daten(self):
        obj = ConsoleView(self.args)
        expected = '\n Daten\n\t 0 : 1\n\t 1 : 2\n\t 2 : 3\n\tAktuelle Box: 1'
        self.assertEqual(expected, obj.render_daten())

    def test_render_optionen(self):
        obj = ConsoleView(self.args)
        expected = ('\n'
                    ' Verfuegbare Zustaende:\n'
                    '\t 0 ZustandStelleUhr : Zustand, zum Stellen der Uhr. (Zurueck zu vorherigem '
                    'Zustand)\n'
                    '\t 1 ZustandStelleUhr : Zustand, zum Stellen der Uhr.\n'
                    ' Verfuegbare Kommandos:\n'
                    "\t's' + Zahl\n"
                    "\t'k' + Zahl\n"
                    "\t't' + Zahl\n"
                    "\t'z' + Zahl\n"
                    "\t'p' + Zahl\n"
                    "\t'r' + Zahl\n"
                    "\t'c' + Zahl\n"
                    '\t')
        self.assertEqual(expected, obj.render_optionen())
