from unittest import TestCase

from src.classes.lerneinheit import LerneinheitJapanisch
from src.classes.vokabelbox import Vokabelbox


class test_vokabelbox(TestCase):

    def setUp(self):
        from src.classes.vokabelkarte import Vokabelkarte

        self.kartenListe = Vokabelkarte.lieferBeispielKarten(100, "Chinesisch")
        self.kartenListe += Vokabelkarte.lieferBeispielKarten(200, "Japanisch")
        self.japBox = Vokabelbox('Japanisch', self.kartenListe[-1].lerneinheit.__class__, [])
        self.chiBox = Vokabelbox('Chinesisch', self.kartenListe[0].lerneinheit.__class__, [])
        self.assertEquals(300, len(self.kartenListe))

    def test_fromdict_asdict(self):
        from src.utils.utils_dataclass import mein_asdict
        
        self.assertEqual(self.japBox, Vokabelbox.fromdict(mein_asdict(self.japBox)))
        self.assertEqual(self.chiBox, Vokabelbox.fromdict(mein_asdict(self.chiBox)))

    def test_kleiner_als(self):
        self.assertLess(self.chiBox, self.japBox)
        liste = [self.japBox, self.chiBox]
        self.assertLess(liste[-1], liste[0])
        sortiert = sorted(liste)
        self.assertLess(sortiert[0], sortiert[-1])

    def test_rename_box(self):
        neuer_name = "JLPT1"
        neue_box = self.japBox.rename(neuer_name)
        self.assertEquals(neuer_name, neue_box.titel)
        self.assertLess(neue_box, self.japBox)

    def test_verfuegbare_frageeinheiten(self):
        result = self.japBox.verfuegbare_frageeinheiten()
        self.assertEquals(4, len(result))
        self.assertEquals("JapanischBedeutung", result[0]().titel())
        obj_a = Vokabelbox('Test', LerneinheitJapanisch, [])
        obj_b = Vokabelbox('Test', LerneinheitJapanisch, [], result[-1])
        self.assertEquals(obj_a.aktuelle_frage().titel(), "JapanischBedeutung")
        self.assertEquals(obj_b.aktuelle_frage().titel(), "JapanischSchreiben")

    def test_ist_erste_frageeinheit(self):
        from src.classes.frageeinheit import Frageeinheit

        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        obj_a = Vokabelbox('Test', LerneinheitJapanisch, [])
        obj_aa = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[1])
        obj_b = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[-1])
        obj_bb = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[3])
        self.assertTrue(obj_a.ist_erste_frageeinheit())
        self.assertFalse(obj_aa.ist_erste_frageeinheit())
        self.assertFalse(obj_b.ist_erste_frageeinheit())
        self.assertFalse(obj_bb.ist_erste_frageeinheit())

    def test_ist_letzte_frageeinheit(self):
        from src.classes.frageeinheit import Frageeinheit

        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        obj_a = Vokabelbox('Test', LerneinheitJapanisch, [])
        obj_aa = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[1])
        obj_b = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[-1])
        obj_bb = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[3])
        self.assertFalse(obj_a.ist_letzte_frageeinheit())
        self.assertFalse(obj_aa.ist_letzte_frageeinheit())
        self.assertTrue(obj_b.ist_letzte_frageeinheit())
        self.assertTrue(obj_bb.ist_letzte_frageeinheit())

    def test_naechste_frageeinheit(self):
        from src.classes.frageeinheit import Frageeinheit

        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        obj_a = Vokabelbox('Test', LerneinheitJapanisch, [])
        obj_aa = obj_a.naechste_frageeinheit()
        obj_b = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[-1])
        obj_bb = obj_b.naechste_frageeinheit()
        self.assertEquals(einheiten[0], obj_a.aktuelle_frage)
        self.assertEquals(einheiten[-1], obj_b.aktuelle_frage)
        self.assertEquals(einheiten[1], obj_aa.aktuelle_frage)
        self.assertEquals(einheiten[0], obj_bb.aktuelle_frage)

    def test_vorherige_frageeinheit(self):
        from src.classes.frageeinheit import Frageeinheit

        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        obj_a = Vokabelbox('Test', LerneinheitJapanisch, [])
        obj_aa = obj_a.vorherige_frageeinheit()
        obj_b = Vokabelbox('Test', LerneinheitJapanisch, [], einheiten[-1])
        obj_bb = obj_b.vorherige_frageeinheit()
        self.assertEquals(einheiten[0], obj_a.aktuelle_frage)
        self.assertEquals(einheiten[-1], obj_b.aktuelle_frage)
        self.assertEquals(einheiten[-1], obj_aa.aktuelle_frage)
        self.assertEquals(einheiten[2], obj_bb.aktuelle_frage)
        self.assertEquals(einheiten[-2], obj_bb.aktuelle_frage)

    def test_filter_vokabelkarten(self):
        from typing import Iterable

        # filter_vokabelkarten() liefert nicht liste, sondern iterable
        result = self.japBox.filter_vokabelkarten(self.kartenListe)
        self.assertIsInstance(result, Iterable)
        self.assertEquals(200, len(list(result)))
        result = self.chiBox.filter_vokabelkarten(self.kartenListe)
        self.assertEquals(100, len(list(result)))
        hsk = []
        for i, elem in enumerate(result):
            if i < 30:
                elem.lerneinheit.daten["HSK"] = 1
            hsk.append(elem)
        self.assertEquals(len(hsk), len(list(result)))
        fun = "('HSK',1) in a.lerneinheit.daten.items()"
        hsk_box = Vokabelbox("HSK 1", self.chiBox.lernklasse, [fun])
        hskresult = hsk_box.filter_vokabelkarten(self.kartenListe)
        self.assertEquals(len(list(hskresult)), 30)
