from unittest import TestCase
from datetime import datetime, timedelta

from src.classes.vokabeltrainermodell import VokabeltrainerModell


class test_vokabeltrainermodell(TestCase):

    def setUp(self):
        from src.classes.vokabelbox import Vokabelbox
        from src.classes.vokabelkarte import Vokabelkarte
        from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
        from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, \
            JSONDateiformatVokabelkarte

        self.liste = Vokabelkarte.lieferBeispielKarten(30, 'LerneinheitChinesisch')
        box = Vokabelbox('Chinesisch', self.liste[0].lerneinheit.__class__, [])
        self.obj = VokabeltrainerModell(vokabelkarten=InMemoryVokabelkartenRepository(dateiname='', verzeichnis=''),
                                        vokabelboxen=InMemeoryVokabelboxRepository())
        self.obj.vokabelboxen.vokabelboxen = [box]*3
        self.obj.vokabelkarten.vokabelkarten = [self.liste]
        self.komplett = VokabeltrainerModell(
            vokabelkarten=InMemoryVokabelkartenRepository(dateiname='_vokabelkarten_2024.JSON',
                                                          verzeichnis='',
                                                          speicher_methode=JSONDateiformatVokabelkarte),
            vokabelboxen=InMemeoryVokabelboxRepository(dateiname='_vokabelboxen_2024.JSON',
                                                       speicher_methode=JSONDateiformatVokabelbox))
        self.komplett.vokabelkarten.laden()
        self.komplett.vokabelboxen.laden()

    def teste_init(self):
        from dataclasses import replace

        self.assertEqual(0, self.komplett.index_aktuelle_box)
        self.assertEqual(83, len(self.komplett.vokabelboxen.vokabelboxen))
        self.assertEqual(3058, len(self.komplett.alle_vokabelkarten()))
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        self.assertEqual('Integrated Chinese Vokabeln Lektion 101', self.komplett.aktuelle_box().titel)

    def test_aktuelle_box(self):
        self.assertEqual(self.komplett.vokabelboxen.vokabelboxen[0],
                         self.komplett.aktuelle_box())
        self.assertEqual(self.komplett.vokabelboxen.vokabelboxen[self.komplett.index_aktuelle_box],
                         self.komplett.aktuelle_box())

    def test_alle_vokabelkarten(self):
        self.assertEqual(self.komplett.vokabelkarten.vokabelkarten,
                         self.komplett.alle_vokabelkarten())

    def test_datum_der_letzten_antwort(self):
        self.assertEqual(1720681644987, VokabeltrainerModell.datum_der_letzten_antwort())
        print(f"\n Datum: {datetime.fromtimestamp(1720681644987 / 1000).strftime('%F %T.%f')}")
