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

# TODO Schreibe noch Tests, die die richtige Funktionalitaet der Uhr prueft. Hatte grosse Probleme,
#  weil in der '='-Hilfsfunktion nicht die Funktion iso_to_millis() aus Lerhnuhr, sondern die Funktion aus datetime
#  benutzt wurde und deshalb Sekunden-Werte in mein Millisekunden-Lernuhrsystem kamen.
