from unittest import TestCase
from vokabelkarte import Vokabelkarte, StatistikManager
from lerneinheit import LerneinheitFactory


class test_vokabelkarte(TestCase):

    def setUp(self):
        self.lernJap = LerneinheitFactory.erzeuge_japanisch_beispiele(anzahl=10)
        self.lernSta = LerneinheitFactory.erzeuge_standard_beispiele(anzahl=10)
        self.vokJap = Vokabelkarte(self.lernJap[0], None, None, None)
        self.vokSta = Vokabelkarte(self.lernSta[0], None, None, None)

    def test_erzeugeStatistik(self):
        self.assertEquals(self.vokJap.lernstats, None)
        self.assertIs(self.vokSta.lernstats, None)
        result = self.vokJap.erzeugeStatistik()
        self.assertIs(type(result.lernstats), StatistikManager)
        self.assertEquals(len(result.lernstats.liste_der_frageeinheiten()), 4)

    def test_erzeugeBeispiele(self):
        result = Vokabelkarte.erzeugeBeispiele(self.lernJap)
        self.assertEquals(len(result), len(self.lernJap))
        [self.assertIs(type(karte), Vokabelkarte) for karte in result]
        [self.assertEquals(len(karte.lernstats.statistiken), 4) for karte in result]
        [self.assertEquals(result[i].lerneinheit, self.lernJap[i]) for i, _ in enumerate(result)]

    def test_lieferBeispielKarten(self):
        liste = Vokabelkarte.lieferBeispielKarten(20, "Japanisch")
        input_list = [("Japanisch", LerneinheitFactory.erzeuge_japanisch_beispiele(1)[0]),
                      ("Chinesisch", LerneinheitFactory.erzeuge_chinesisch_beispiele(1)[0]),
                      ("Kanji", LerneinheitFactory.erzeuge_japanisch_kanji_beispiele(1)[0]),
                      ("Sonstiges", LerneinheitFactory.erzeuge_standard_beispiele(1)[0])]
        self.assertEquals(len(liste), 20)
        for sprache, lernE in input_list:
            [self.assertEquals(type(elem.lerneinheit), type(lernE)) for elem in
             Vokabelkarte.lieferBeispielKarten(20, sprache)]
