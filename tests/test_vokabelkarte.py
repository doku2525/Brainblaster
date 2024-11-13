from unittest import TestCase
from vokabelkarte import Vokabelkarte, StatistikManager
from lerneinheit import LerneinheitFactory

from antwort import Antwort
from dataclasses import replace, asdict

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

    def test_nicht_besonderes(self):
        # TODO Aktuelles Problem
        #   Implementiere Weg, um einer Vokabelkarte eine Antwort der aktuellen Frageeinheit hinzuzufuegen.
        liste = Vokabelkarte.lieferBeispielKarten(20, "Japanisch")
        print(f"\n Zeile 1: {liste[0].__dict__}")
        f = liste[0].lernstats.suche_frageeinheit_nach_titel(liste[0].lernstats.titel_der_frageeinheiten()[0])
        print(f"\nZeile 2: {replace(liste[0].lernstats.statistiken[f], antworten=[1,2,3,4])}")
        print(f"\nZeile 3: {liste[0].lernstats.statistiken[f].add_neue_antwort(Antwort(5,10))}")
        neue_stat = liste[0].lernstats.statistiken[f].add_neue_antwort(Antwort(5,10))
        neuer_sm = {key : neue_stat if key == f else value for key, value in liste[0].lernstats.statistiken.items()}
        print(f"Zeile 4: Neuer Manager{neuer_sm}")
        print(f"Zeile 5: {replace(liste[0], lernstats=replace(liste[0].lernstats, statistiken=neuer_sm))}")
        print(f"Zeile 6: AS: {asdict(liste[0])}")
        print(f"Zeile 7: DI: {liste[0].__dict__}")