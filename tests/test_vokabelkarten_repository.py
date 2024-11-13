from unittest import TestCase
import copy

from src.repositories.vokabelkarten_repository import (InMemoryVokabelkartenRepository,
                                                       BINARYDateiformatVokabelkarte, JSONDateiformatVokabelkarte)
from src.classes.vokabelkarte import Vokabelkarte


class test_VokabelkartenRepository(TestCase):

    def setUp(self):
        self.karten = Vokabelkarte.lieferBeispielKarten(anzahl=20, sprache="Japanisch")
        self.repo = InMemoryVokabelkartenRepository(dateiname="__vokabelkarten.data",
                                                    verzeichnis="",
                                                    vokabelkarten=self.karten[:10],
                                                    speicher_methode=BINARYDateiformatVokabelkarte)
        self.assertEqual(self.karten[:10], self.repo.vokabelkarten)
        self.assertEqual(10, len(self.repo.vokabelkarten))

    def test_speichern(self):
        self.repo.speichern()

    def test_laden(self):
        neues_repo = copy.deepcopy(self.repo)
        neues_repo.vokabelkarten = []
        self.assertNotEqual(neues_repo.vokabelkarten, self.repo)
        neues_repo.laden()
        self.assertEqual(len(neues_repo.vokabelkarten), len(self.repo.vokabelkarten))
        self.assertEqual([l_einheit.lerneinheit.eintrag for l_einheit in neues_repo.vokabelkarten],
                         [l_einheit.lerneinheit.eintrag for l_einheit in self.repo.vokabelkarten])
        neues_repo.vokabelkarten = self.karten[:1]
        self.assertEqual(1, len(neues_repo.vokabelkarten))
        neues_repo.laden()          # Nicht leer, deshalb nicht ueberschreiben
        self.assertEqual(1, len(neues_repo.vokabelkarten))

    def test_erneut_laden(self):
        neues_repo = copy.deepcopy(self.repo)
        neues_repo.vokabelkarten = []
        self.assertNotEqual(neues_repo.vokabelkarten, self.repo)
        neues_repo.laden()
        neues_repo.vokabelkarten = self.karten[:1]
        self.assertEqual(1, len(neues_repo.vokabelkarten))
        neues_repo.erneut_laden()          # Nicht leer, deshalb nicht ueberschreiben
        self.assertEqual(10, len(neues_repo.vokabelkarten))

    def test_add_karte(self):
        self.assertFalse(self.repo.add_karte(self.karten[0]))
        self.assertEqual(self.repo.vokabelkarten[-1], self.karten[9])
        self.assertTrue(self.repo.add_karte(self.karten[10]))
        self.assertEqual(self.repo.vokabelkarten[-1], self.karten[10])

    def test_remove_karte(self):
        self.repo.remove_karte(self.karten[10])
        self.assertEqual(10, len(self.repo.vokabelkarten))
        self.repo.remove_karte(self.karten[9])
        self.assertEqual(9, len(self.repo.vokabelkarten))
        self.repo.remove_karte(self.karten[0])
        self.assertEqual(self.repo.vokabelkarten[0], self.karten[1])

    def test_replace_karte(self):
        self.repo.replace_karte(self.karten[10], self.karten[11])
        self.assertEqual(self.karten[:10], self.repo.vokabelkarten)
        self.repo.replace_karte(self.karten[0], self.karten[10])
        self.assertEqual(10, len(self.repo.vokabelkarten))
        self.assertEqual(self.repo.vokabelkarten[0], self.karten[10])
        self.repo.replace_karte(self.karten[1], self.karten[10])
        self.assertEqual(10, len(self.repo.vokabelkarten))
        self.assertEqual(self.repo.vokabelkarten[1], self.karten[1])

    def test_exists_karte(self):
        self.assertTrue(self.repo.exists_karte(self.karten[5]))
        self.assertFalse(self.repo.exists_karte(self.karten[15]))

    def test_json_speichern_laden(self):
        self.repo.speicher_methode = JSONDateiformatVokabelkarte
        self.repo.dateiname = '__vokabelkarten.JSON'
        self.repo.vokabelkarten = self.karten[:2]
        self.repo.speichern()
        self.repo.erneut_laden()
        self.assertEqual(self.repo.vokabelkarten, self.karten[:2])
