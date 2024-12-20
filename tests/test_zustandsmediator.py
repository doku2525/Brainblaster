from unittest import TestCase
from dataclasses import replace

from src.classes.zustandsmediator import ZustandsMediator


class test_ZustandsMediator(TestCase):

    def setUp(self):
        pass

    def test_init(self):
        obj = ZustandsMediator()
        [self.assertEqual('Zustand', key[:7]) for key, _ in obj.klassen.items()]
        [self.assertIn(value, ZustandsMediator.__subclasses__()) for _, value in obj.klassen.items()]

    def test_zustand_console_view_zustandende(self):
        from src.classes.zustand import ZustandENDE

        obj = ZustandsMediator()
        result = obj.zustand_to_consoleview_data(ZustandENDE(aktuelle_zeit='test'), 0)
        self.assertIsInstance(result, dict)
        self.assertEqual('ZustandENDE', result['zustand'])
        self.assertEqual('test', result['aktuelle_zeit'])
        self.assertEqual(None, result.get('daten', None))
        self.assertEqual('Ciao! None', result['optionen'])

    def test_zustand_console_view_zustandstart(self):
        from src.classes.zustand import ZustandStart

        obj = ZustandsMediator()
        zustand_ohne_parrent = ZustandStart(liste=["1", "2", "3"], aktueller_index=0, aktuelle_zeit='test')
        result = obj.zustand_to_consoleview_data(zustand_ohne_parrent, 0)
        expected_data_str = ' 0 : 1\n 1 : 2\n 2 : 3\nAktuelle Box: 1'
        expected_optionen_str = " 1 ENDE : Beende Programm\n'+' + Zahl\n'-' + Zahl\n'=' + Zahl\n"
        self.assertIsInstance(result, dict)
        self.assertEqual('ZustandStart', result['zustand'])
        self.assertEqual('test', result['aktuelle_zeit'])
        self.assertEqual(expected_data_str, result['daten'])
        self.assertEqual(expected_optionen_str, result['optionen'])

        zustand_mit_parrent = replace(zustand_ohne_parrent, parent=ZustandStart())
        # Da ZustandStart per Definition kein parent-Zustand hat, veraendert sich nichts.
        result = obj.zustand_to_consoleview_data(zustand_mit_parrent, 0)
        self.assertEqual('ZustandStart', result['zustand'])
        self.assertEqual('test', result['aktuelle_zeit'])
        self.assertEqual(expected_data_str, result['daten'])
        self.assertEqual(expected_optionen_str, result['optionen'])

        zustand_mit_zwei_children = replace(zustand_mit_parrent, child=zustand_mit_parrent.child * 2)
        result = obj.zustand_to_consoleview_data(zustand_mit_zwei_children, 0)
        expected_optionen_str = (" 1 ENDE : Beende Programm\n 2 ENDE : Beende Programm\n'" +
                                 "+' + Zahl\n'-' + Zahl\n'=' + Zahl\n")
        self.assertEqual('ZustandStart', result['zustand'])
        self.assertEqual('test', result['aktuelle_zeit'])
        self.assertEqual(expected_data_str, result['daten'])
        self.assertEqual(expected_optionen_str, result['optionen'])

    def test_zustand_console_view_zustandveraenderlernuhr(self):
        from src.classes.zustand import ZustandVeraenderLernuhr, ZustandStart
        from src.classes.lernuhr import Lernuhr

        obj = ZustandsMediator()
        zustand_ohne_parrent = ZustandVeraenderLernuhr(aktuelle_zeit='2024-12-19 15:10:42', neue_uhr=Lernuhr())
        result = obj.zustand_to_consoleview_data(zustand_ohne_parrent, 0)
        expected_data_str = ['Neue Uhrzeit: 2024-12-19 15:10:42.534000', 'Startzeit : 0',
                             'Kalkulationszeit : 0', 'Tempo : 1.0', 'Modus : UhrStatus.ECHT', '']
        expected_optionen_str = ("'s' + Zahl\n"
                                 "'k' + Zahl\n"
                                 "'t' + Zahl\n"
                                 "'z' + Zahl\n"
                                 "'p' + Zahl\n"
                                 "'r' + Zahl\n"
                                 "'c' + Zahl\n")
        self.assertIsInstance(result, dict)
        self.assertEqual('Lernuhr', zustand_ohne_parrent.neue_uhr.__class__.__name__)
        self.assertEqual('ZustandVeraenderLernuhr', result['zustand'])
        self.assertEqual('2024-12-19 15:10:42', result['aktuelle_zeit'])
        for index, wert in enumerate(expected_data_str):
            if index == 0:
                self.assertEqual(len(wert), len(result['daten'].split('\n')[index]))
                self.assertIn(wert[:15], result['daten'].split('\n')[index])
            else:
                self.assertEqual(wert, result['daten'].split('\n')[index])
        self.assertEqual(expected_optionen_str, result['optionen'])

        zustand_mit_parrent = replace(zustand_ohne_parrent, parent=zustand_ohne_parrent)
        # Beim hinzufuegen von Parents zur Lernuhr wird automatisch der gleiche Zustand als Child hinzugefuegt,
        #   um entweder zum parent zurueck zu gehen ohne zu speichern oder zum child zu gehen und die
        #   Veraenderungen in Lernuhr zu speichern
        result = obj.zustand_to_consoleview_data(zustand_mit_parrent, 0)
        expected_optionen_str = (
            ' 0 ZustandStelleUhr : Zustand, zum Stellen der Uhr.\n'
            ' 1 ZustandStelleUhr : Zustand, zum Stellen der Uhr.\n') + expected_optionen_str
        self.assertIsInstance(result, dict)
        self.assertEqual('Lernuhr', zustand_ohne_parrent.neue_uhr.__class__.__name__)
        self.assertEqual('ZustandVeraenderLernuhr', result['zustand'])
        self.assertEqual('2024-12-19 15:10:42', result['aktuelle_zeit'])
        for index, wert in enumerate(expected_data_str):
            if index == 0:
                self.assertEqual(len(wert), len(result['daten'].split('\n')[index]))
                self.assertIn(wert[:15], result['daten'].split('\n')[index])
            else:
                self.assertEqual(wert, result['daten'].split('\n')[index])
        self.assertEqual(expected_optionen_str, result['optionen'])

        zustand_mit_cild = replace(zustand_ohne_parrent, child=[ZustandStart()])
        # Es kann kein Child ohne parent hinzugefuegt werden, da es keine weiteren Child als Zurueck mit speichern gibt
        result = obj.zustand_to_consoleview_data(zustand_mit_cild, 0)
        expected_optionen_str = '\n'.join(expected_optionen_str.split("\n")[2:])  # Entferne Zeilen Option "0" und "1"
        self.assertIsInstance(result, dict)
        self.assertEqual('Lernuhr', zustand_ohne_parrent.neue_uhr.__class__.__name__)
        self.assertEqual('ZustandVeraenderLernuhr', result['zustand'])
        self.assertEqual('2024-12-19 15:10:42', result['aktuelle_zeit'])
        for index, wert in enumerate(expected_data_str):
            if index == 0:
                self.assertEqual(len(wert), len(result['daten'].split('\n')[index]))
                self.assertIn(wert[:15], result['daten'].split('\n')[index])
            else:
                self.assertEqual(wert, result['daten'].split('\n')[index])
        self.assertEqual(expected_optionen_str, result['optionen'])

    def test_zustand_flask_view_zustandende(self):
        from src.classes.zustand import ZustandENDE

        obj = ZustandsMediator()
        result = obj.zustand_to_flaskview_data(ZustandENDE(aktuelle_zeit='test'), 0)
        self.assertIsInstance(result, dict)
        self.assertEqual('ZustandENDE', result['zustand'])
        self.assertEqual('test', result['aktuelle_uhrzeit'])
        self.assertEqual(2, len(result.keys()))

    def test_zustand_flask_view_zustandstart(self):
        from src.classes.zustand import ZustandStart

        obj = ZustandsMediator()
        ausgangs_liste = ["1", "2", "3"]
        ausgangs_index = 0
        zustand_ohne_parrent = ZustandStart(liste=ausgangs_liste, aktueller_index=ausgangs_index, aktuelle_zeit='test')
        result = obj.zustand_to_flaskview_data(zustand_ohne_parrent, 0)
        self.assertIsInstance(result, dict)
        self.assertEqual('ZustandStart', result['zustand'])
        self.assertEqual('test', result['aktuelle_uhrzeit'])
        self.assertEqual(ausgangs_liste, result['liste'])
        self.assertEqual(ausgangs_index, result['aktueller_index'])

        zustand_mit_parrent = replace(zustand_ohne_parrent, parent=ZustandStart())
        # Da an die Flaskview keine Zustaende, sondern nur Daten uebergeben werden, sollte die Test erfolgreich sein.
        result = obj.zustand_to_flaskview_data(zustand_mit_parrent, 0)
        self.assertIsInstance(result, dict)
        self.assertEqual('ZustandStart', result['zustand'])
        self.assertEqual('test', result['aktuelle_uhrzeit'])
        self.assertEqual(ausgangs_liste, result['liste'])
        self.assertEqual(ausgangs_index, result['aktueller_index'])

        zustand_mit_zwei_children = replace(zustand_mit_parrent, child=zustand_mit_parrent.child * 2)
        # Da an die Flaskview keine Zustaende, sondern nur Daten uebergeben werden, sollte die Test erfolgreich sein.
        result = obj.zustand_to_flaskview_data(zustand_mit_zwei_children,0)
        self.assertIsInstance(result, dict)
        self.assertEqual('ZustandStart', result['zustand'])
        self.assertEqual('test', result['aktuelle_uhrzeit'])
        self.assertEqual(ausgangs_liste, result['liste'])
        self.assertEqual(ausgangs_index, result['aktueller_index'])

    def test_zustand_flask_view_zustandveraenderlernuhr(self):
        from src.classes.zustand import ZustandVeraenderLernuhr
        from src.classes.zustand import Lernuhr

        obj = ZustandsMediator()
        zeit = '1970-01-01 01:01:01'
        zustand_ohne_parrent = ZustandVeraenderLernuhr(aktuelle_zeit=zeit, neue_uhr=Lernuhr())
        result = obj.zustand_to_flaskview_data(zustand_ohne_parrent, 0)

        self.assertIsInstance(result, dict)
        self.assertEqual('Lernuhr', zustand_ohne_parrent.neue_uhr.__class__.__name__)
        self.assertEqual('ZustandVeraenderLernuhr', result['zustand'])
        self.assertEqual(zeit, result['aktuelle_uhrzeit'])
        self.assertEqual(len(zeit), len(result['neue_uhrzeit'][:-7]))
        self.assertEqual(len(zeit.split()), len(result['neue_uhrzeit'][:-7].split()))
        self.assertIsInstance(result['neue_uhr'], dict)
        expected_neue_uhr = {'kalkulations_zeit': '1970-01-01 01:00:00.000000',
                             'start_zeit': '1970-01-01 01:00:00.000000', 'tempo': 1.0, 'pause': 0, 'modus': 'ECHT'}
        self.assertEqual(expected_neue_uhr, result['neue_uhr'])
