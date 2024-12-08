from unittest import TestCase
from unittest.mock import patch, call, ANY

from src.classes.zustand import Zustand, ZustandENDE, ZustandStart


class test_Zustand(TestCase):

    def test_init(self):
        objekt = Zustand()
        self.assertIsInstance(objekt, Zustand)
        self.assertEqual('', objekt.titel)
        self.assertEqual('', objekt.beschreibung)
        self.assertIsNone(objekt.parent)
        self.assertEqual([], objekt.child)
        self.assertEqual([], objekt.kommandos)
        self.assertEqual({}, objekt.data)

    def test_init_zustand_start(self):
        objekt = ZustandStart()
        self.assertIsInstance(objekt, ZustandStart)
        self.assertIsInstance(objekt, Zustand)
        self.assertEqual('Zustand 1', objekt.titel)
        self.assertEqual('Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.',
                         objekt.beschreibung)
        self.assertIsNone(objekt.parent)
        self.assertEqual(1, len(objekt.child))
        self.assertEqual((ZustandENDE(),), objekt.child)
        self.assertEqual(("+", "-", "="), objekt.kommandos)
        self.assertEqual({}, objekt.data)
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])
        self.assertEqual({'aktueller_index': 0, 'liste': ["A", "B"]}, objekt.data)

    def test_init_zustand_ende(self):
        objekt = ZustandENDE()
        self.assertIsInstance(objekt, ZustandENDE)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('ENDE', objekt.titel)
        self.assertEqual('Beende Programm',objekt.beschreibung)

    def test_daten_text_konsole(self):
        objekt = Zustand()
        self.assertIsNone(objekt.daten_text_konsole())
        self.assertIsNone(objekt.daten_text_konsole(lambda x: None))

    def test_daten_text_konsole_zustand_start(self):
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])
        expected_output = (' Zustand 1\n' +
                           '\t Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.\n' +
                           ' 0 : A\n' +
                           ' 1 : B\n' +
                           ' Aktuelle Box: A')
        self.assertIsNotNone(objekt.daten_text_konsole())
        self.assertEqual(expected_output, objekt.daten_text_konsole())
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B", "C"])
        expected_output = (' Zustand 1\n' +
                           '\t Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.\n' +
                           ' 0 : A\n' +
                           ' 1 : B\n' +
                           ' 2 : C\n' +
                           ' Aktuelle Box: A')
        self.assertEqual(expected_output, objekt.daten_text_konsole())

    def test_info_text_konsole(self):
        objekt = Zustand()
        expected_output = ("----------\n" +
                           "* Die verfuegbaren Zustaende\n" +
                           "* Die verfuegbaren Kommandos\n")
        self.assertEqual(expected_output, objekt.info_text_konsole())

    def test_info_text_konsole_zustand_start(self):
        objekt = ZustandStart()
        expected_output = ("----------\n" +
                           "* Die verfuegbaren Zustaende\n" +
                           "\t0 ENDE : Beende Programm\n" +
                           "* Die verfuegbaren Kommandos\n" +
                           "\t'+' + Zahl\n" +
                           "\t'-' + Zahl\n" +
                           "\t'=' + Zahl\n")
        self.assertEqual(expected_output, objekt.info_text_konsole())

    def test_verarbeite_userinput(self):
        objekt = Zustand()
        result, fun, args = objekt.verarbeite_userinput('')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)

    def test_verarbeite_userinput_zustand_start(self):
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])
        result, fun, args = objekt.verarbeite_userinput('')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        result, fun, args = objekt.verarbeite_userinput('+1')
        self.assertNotEqual(result, objekt)
        self.assertEqual(result.aktueller_index, 1)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        result, fun, args = objekt.verarbeite_userinput('+5')
        self.assertEqual(result.aktueller_index, 1)
        result, fun, args = objekt.verarbeite_userinput('-5')
        self.assertEqual(result.aktueller_index, 0)
        result, fun, args = objekt.verarbeite_userinput('=1')
        self.assertEqual(result.aktueller_index, 1)
