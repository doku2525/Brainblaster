from unittest import TestCase
from unittest.mock import patch, call, ANY
from dataclasses import replace
from typing import Callable, cast

from src.zustaende.zustand import Zustand, ZustandENDE, ZustandBoxinfo
from src.zustaende.zustandstart import ZustandStart
from src.zustaende.zustandveraenderlernuhr import ZustandVeraenderLernuhr
from src.zustaende.zustandvokabeltesten import ZustandVokabelTesten


class test_Zustand(TestCase):

    def test_init(self):
        objekt = Zustand()
        self.assertIsInstance(objekt, Zustand)
        self.assertEqual('', objekt.titel)
        self.assertEqual('', objekt.beschreibung)
        self.assertIsNone(objekt.parent)
        self.assertEqual([], objekt.child)
        self.assertEqual([], objekt.kommandos)

    def test_init_zustand_ende(self):
        objekt = ZustandENDE()
        self.assertIsInstance(objekt, ZustandENDE)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('ENDE', objekt.titel)
        self.assertEqual('Beende Programm', objekt.beschreibung)

    def test_init_zustand_boxinfo(self):
        objekt = ZustandBoxinfo()
        self.assertIsInstance(objekt, ZustandBoxinfo)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('Zustand 2', objekt.titel)
        self.assertEqual('Zustand 2, Zeigt die Boxinfos der aktuellen Box an.', objekt.beschreibung)
        self.assertEqual({}, objekt.info)
        self.assertEqual('', objekt.box_titel)
        self.assertEqual('', objekt.aktuelle_frageeinheit)

    def test_verarbeite_userinput(self):
        objekt = Zustand()
        result, fun, args = objekt.verarbeite_userinput('')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)

    def test_position_index_zustand_in_child(self):
        objekt = Zustand()      # child = []
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen('Irgendwas'))
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen('ZustandENDE'))
        objekt = Zustand(child=[ZustandStart(), ZustandVeraenderLernuhr(), ZustandENDE()])
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen(''))
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen('Irgendwas'))
        self.assertEqual('1', objekt.position_zustand_in_child_mit_namen('ZustandStart'))
        self.assertEqual('2', objekt.position_zustand_in_child_mit_namen('ZustandVeraenderLernuhr'))
        self.assertEqual('3', objekt.position_zustand_in_child_mit_namen('ZustandENDE'))

    def test_verarbeite_userinput_mit_zustandsnamen(self):
        objekt = Zustand()      # child = []
        self.assertEqual(objekt, objekt.verarbeite_userinput('@Irgendwas')[0])
        objekt = Zustand(child=[ZustandStart(), ZustandVeraenderLernuhr(), ZustandENDE()])
        self.assertIsInstance(objekt.verarbeite_userinput('@ZustandStart')[0], ZustandStart)
        self.assertIsInstance(objekt.verarbeite_userinput('@ZustandVeraenderLernuhr')[0], ZustandVeraenderLernuhr)
        self.assertIsInstance(objekt.verarbeite_userinput('@ZustandENDE')[0], ZustandENDE)

# TODO Schreibe noch Tests, die die richtige Funktionalitaet der Uhr prueft. Hatte grosse Probleme,
#  weil in der '='-Hilfsfunktion nicht die Funktion iso_to_millis() aus Lerhnuhr, sondern die Funktion aus datetime
#  benutzt wurde und deshalb Sekunden-Werte in mein Millisekunden-Lernuhrsystem kamen.
