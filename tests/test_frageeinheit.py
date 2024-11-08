from unittest import TestCase
from frageeinheit import Frageeinheit, FrageeinheitJapanischBedeutung, FrageeinheitJapanischSchreiben
from lerneinheit import LerneinheitStandard, LerneinheitJapanisch


class test_Frageeinheit(TestCase):

    def setUp(self):
        pass
        self.standardFragen = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitStandard)
        self.standardJapanisch = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)

    def test_kleiner_als(self):
        obja = FrageeinheitJapanischBedeutung()
        objb = FrageeinheitJapanischSchreiben()
        self.assertLess(obja, objb)
        result = sorted([elem() for elem in self.standardJapanisch])
        self.assertEquals(1, result[0].rank)
        self.assertEquals(4, result[-1].rank)

    def test_alle_frageeinheiten(self):
        [self.assertTrue(issubclass(cls, Frageeinheit), f"{cls} keine Subclass")
         for cls
         in Frageeinheit.alle_frageeinheiten()]

    def test_titel(self):
        result = [cls().titel() for cls in Frageeinheit.alle_frageeinheiten()]
        self.assertGreaterEqual(len([elem for elem in result if "Standard" in elem]), 2)
        self.assertGreaterEqual(len([elem for elem in result if "Japanisch" in elem]), 8)
        self.assertGreaterEqual(len([elem for elem in result if "Kanji" in elem]), 4)
        self.assertGreaterEqual(len([elem for elem in result if "Chinesisch" in elem]), 4)

    def test_suche_frageeinheiten_der_lernklasse(self):
        self.assertEquals(2, len(self.standardFragen), "LerneinheitStandard hat 2 Frageeinheiten")
        print(self.standardJapanisch)
        self.assertEquals(4, len(self.standardJapanisch), "LerneinheitJapanisch hat 4 Frageeinheiten")
        self.assertEquals(
            self.standardJapanisch[0]().rank,
            min([elem().rank for elem in self.standardJapanisch]),
            "Die erste Frage hat den niedrigsten Rank")
        self.assertEquals(
            self.standardJapanisch[-1]().rank,
            max([elem().rank for elem in self.standardJapanisch]),
            "Die letzte Frage hat den hoechsten Rank")

    def test_suche_frageeinheit_fuer_lernklasse_mit_titel(self):
        titel = self.standardJapanisch[0]().titel()
        self.assertEquals(self.standardJapanisch[0],
                          Frageeinheit().suche_frageeinheit_fuer_lernklasse_mit_titel(LerneinheitJapanisch, titel),
                          "Richtige Frageeinheit gefunden.")

    def test_ist_erste_frageeinheit(self):
        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        self.assertTrue(Frageeinheit.ist_erste_frageeinheit(einheiten[0]))
        self.assertFalse(Frageeinheit.ist_erste_frageeinheit(einheiten[-1]))
        self.assertFalse(Frageeinheit.ist_erste_frageeinheit(einheiten[1]))

    def test_ist_letzte_frageeinheit(self):
        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        self.assertTrue(Frageeinheit.ist_letzte_frageeinheit(einheiten[-1]))
        self.assertTrue(Frageeinheit.ist_letzte_frageeinheit(einheiten[3]))
        self.assertFalse(Frageeinheit.ist_letzte_frageeinheit(einheiten[0]))
        self.assertFalse(Frageeinheit.ist_letzte_frageeinheit(einheiten[1]))

    def test_vorherige_frageeinheit(self):
        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        self.assertEquals(einheiten[0], Frageeinheit.vorherige_frageeinheit(einheiten[1]))
        self.assertEquals(einheiten[-1], Frageeinheit.vorherige_frageeinheit(einheiten[0]))
        self.assertEquals(einheiten[-2], Frageeinheit.vorherige_frageeinheit(einheiten[-1]))

    def test_folgende_frageeinheit(self):
        einheiten = Frageeinheit.suche_frageeinheiten_der_lernklasse(LerneinheitJapanisch)
        self.assertEquals(einheiten[0], Frageeinheit.folgende_frageeinheit(einheiten[-1]))
        self.assertEquals(einheiten[0], Frageeinheit.folgende_frageeinheit(einheiten[3]))
        self.assertEquals(einheiten[1], Frageeinheit.folgende_frageeinheit(einheiten[0]))
