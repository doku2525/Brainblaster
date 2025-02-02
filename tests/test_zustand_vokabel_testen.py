from unittest import TestCase
from unittest.mock import patch, call, ANY
from dataclasses import replace
from typing import Callable, cast

from src.zustaende.zustand import Zustand, ZustandENDE, ZustandBoxinfo
from src.zustaende.zustandstart import ZustandStart
from src.zustaende.zustandveraenderlernuhr import ZustandVeraenderLernuhr
from src.zustaende.zustandvokabeltesten import ZustandVokabelTesten


class test_ZustandVokabelTesten(TestCase):

    def test_init_zustand_vokabel_testen(self):
        objekt = ZustandVokabelTesten()
        self.assertIsInstance(objekt, ZustandVokabelTesten)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('Zustand Testen', objekt.titel)
        self.assertEqual('Zustand Testen, fuehrt die Tests aus und verarbeitet Antworten', objekt.beschreibung)
        self.assertEqual([], objekt.input_liste)
        self.assertEqual([], objekt.output_liste)
        self.assertIsNone(objekt.aktuelle_frageeinheit)
        self.assertTrue(objekt.wiederholen)
        self.assertEqual('', objekt.aktuelle_zeit)

    def test_parse_user_eingabe_option_a_richtige_antwort(self):
        from src.classes.vokabelkarte import Vokabelkarte

        class MockObjekt(Vokabelkarte):
            def neue_antwort(self, frage_einheit, antwort):
                return antwort

        karte = MockObjekt()
        objekt = ZustandVokabelTesten(input_liste=[karte])

        fun, args = objekt.parse_user_eingabe(list('a6'))
        zustand = args[0]
        karten = args[1]
        self.assertNotEqual(zustand, objekt)
        self.assertIsInstance(zustand, ZustandVokabelTesten)
        self.assertEqual('CmdTestErgebnis', fun)
        self.assertEqual([], zustand.input_liste)
        self.assertEqual([], zustand.output_liste)
        self.assertEqual(2, len(args))
        self.assertEqual(karte, karten[0])
        # Fuehre Funktion neue_karte mit zeit = 0 aus.
        self.assertEqual('Antwort', karten[1](0).__class__.__name__)
        self.assertEqual(6, karten[1](0).antwort)
        self.assertEqual(0, karten[1](0).erzeugt)

    def test_parse_user_eingabe_option_a_falsche_antwort(self):
        from src.classes.vokabelkarte import Vokabelkarte

        class MockObjekt(Vokabelkarte):
            def neue_antwort(self, frage_einheit, antwort):
                return antwort

        karte = MockObjekt()
        objekt = ZustandVokabelTesten(input_liste=[karte])

        fun, args = objekt.parse_user_eingabe(list('a2'))
        zustand = args[0]
        karten = args[1]
        self.assertNotEqual(zustand, objekt)
        self.assertIsInstance(zustand, ZustandVokabelTesten)
        self.assertEqual('CmdTestErgebnis', fun)
        self.assertEqual([], zustand.input_liste)
        self.assertEqual([karte], zustand.output_liste)
        self.assertEqual(2, len(args))
        self.assertEqual(karte, karten[0])
        # Fuehre Funktion neue_karte mit zeit = 0 aus.
        self.assertEqual('Antwort', karten[1](0).__class__.__name__)
        self.assertEqual(2, karten[1](0).antwort)
        self.assertEqual(0, karten[1](0).erzeugt)

    def test_parse_user_eingabe_option_a_falsche_antwort_wiederholen_false(self):
        from src.classes.vokabelkarte import Vokabelkarte

        class MockObjekt(Vokabelkarte):
            def neue_antwort(self, frage_einheit, antwort):
                return antwort

        karte = MockObjekt()
        objekt = ZustandVokabelTesten(input_liste=[karte], wiederholen=False)

        fun, args = objekt.parse_user_eingabe(list('a2'))
        zustand = args[0]
        karten = args[1]
        self.assertNotEqual(zustand, objekt)
        self.assertIsInstance(zustand, ZustandVokabelTesten)
        self.assertEqual('CmdTestErgebnis', fun)
        self.assertEqual([], zustand.input_liste)
        self.assertEqual([], zustand.output_liste)
        self.assertEqual(2, len(args))
        self.assertEqual(karte, karten[0])
        # Fuehre Funktion neue_karte mit zeit = 0 aus.
        self.assertEqual('Antwort', karten[1](0).__class__.__name__)
        self.assertEqual(2, karten[1](0).antwort)
        self.assertEqual(0, karten[1](0).erzeugt)

    def test_parse_user_eingabe_option_a_mit_leerem_string(self):
        from src.classes.vokabelkarte import Vokabelkarte

        class MockObjekt(Vokabelkarte):
            def neue_antwort(self, frage_einheit, antwort):
                return antwort

        karte = MockObjekt()
        objekt = ZustandVokabelTesten()

        fun, args = objekt.parse_user_eingabe(list(''))
        self.assertEqual('', fun)
        self.assertEqual(tuple(), args)

    def test_parse_user_eingabe_option_a_richtig_mit_leerer_input_liste(self):
        from src.classes.vokabelkarte import Vokabelkarte

        class MockObjekt(Vokabelkarte):
            def neue_antwort(self, frage_einheit, antwort):
                return antwort

        karte = MockObjekt()
        objekt = ZustandVokabelTesten(output_liste=[karte])

        fun, args = objekt.parse_user_eingabe(list('a6'))
        zustand = args[0]
        karten = args[1]
        self.assertNotEqual(zustand, objekt)
        self.assertIsInstance(zustand, ZustandVokabelTesten)
        self.assertEqual('CmdTestErgebnis', fun)
        self.assertEqual(tuple(), karten)
        self.assertEqual([], zustand.output_liste)
        self.assertEqual([], zustand.input_liste)

    def test_parse_user_eingabe_option_a_falsch_mit_leerer_input_liste(self):
        from src.classes.vokabelkarte import Vokabelkarte

        class MockObjekt(Vokabelkarte):
            def neue_antwort(self, frage_einheit, antwort):
                return antwort

        karte_eins = MockObjekt(erzeugt=1)
        karte_zwei = MockObjekt(erzeugt=2)
        objekt = ZustandVokabelTesten(output_liste=[karte_eins, karte_zwei])

        fun, args = objekt.parse_user_eingabe(list('a2'))
        zustand = args[0]
        karten = args[1]
        self.assertNotEqual(zustand, objekt)
        self.assertIsInstance(zustand, ZustandVokabelTesten)
        self.assertEqual('CmdTestErgebnis', fun)
        self.assertEqual(tuple(), karten)
        self.assertEqual([karte_zwei, karte_eins], zustand.output_liste)
        self.assertEqual([], zustand.input_liste)
