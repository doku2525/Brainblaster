from unittest import TestCase
from src.classes.vokabelkarte import Vokabelkarte, KartenStatus
from src.classes.lerneinheit import LerneinheitFactory
from src.classes.statistikmanager import StatistikManager
from src.utils.utils_dataclass import mein_asdict


class test_vokabelkarte(TestCase):

    def setUp(self):
        self.lernJap = LerneinheitFactory.erzeuge_japanisch_beispiele(anzahl=10)
        self.lernSta = LerneinheitFactory.erzeuge_standard_beispiele(anzahl=10)
        self.vokJap = Vokabelkarte(lerneinheit=self.lernJap[0])
        self.vokSta = Vokabelkarte(lerneinheit=self.lernSta[0])

    def test_fromdict(self):
        sprachen = ["Japanisch", "Chineisch", "Kanji"]
        for sprache in sprachen:
            karten_liste = Vokabelkarte.lieferBeispielKarten(1, sprache)
            self.assertEquals(karten_liste[0], Vokabelkarte.fromdict(mein_asdict(karten_liste[0])))

    def test_erzeugeStatistik(self):
        self.assertIsInstance(self.vokJap.lernstats, StatistikManager)
        self.assertIsInstance(self.vokJap.status, KartenStatus)
        result = self.vokJap.erzeugeStatistik()
        self.assertIsInstance(result.lernstats, StatistikManager)
        self.assertIsInstance(result.status, KartenStatus)
        self.assertEquals(result.status, KartenStatus.NORMAL)
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
