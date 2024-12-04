from unittest import TestCase
from typing import cast
from src.classes.kartenfilter import (KartenfilterTupel, FilterKartenstatistik, KartenfilterStrategie, FilterMischen,
                                      FilterKartenanzahl)
from src.classes.vokabeltrainermodell import VokabeltrainerModell
from src.classes.vokabelkarte import Vokabelkarte
from src.classes.vokabelbox import Vokabelbox
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository
from src.classes.statistikfilter import StatistikfilterNeue, StatistikfilterPruefen
from src.classes.lerneinheit import LerneinheitChinesisch


class test_Kartenfilter(TestCase):

    def setUp(self):
        self.liste = Vokabelkarte.lieferBeispielKarten(30, 'LerneinheitChinesisch')
        box = Vokabelbox('Chinesisch', self.liste[0].lerneinheit.__class__, [])
        self.obj = VokabeltrainerModell(vokabelkarten=InMemoryVokabelkartenRepository(dateiname='', verzeichnis=''),
                                        vokabelboxen=InMemeoryVokabelboxRepository())
        self.obj.vokabelboxen.vokabelboxen = [box]*3
        self.obj.vokabelkarten.vokabelkarten = [self.liste]

    def test_gefilterte_karten(self):
        def mein_filter(nummer: int, karten_liste: list[int]):
            return [nummer + elem for elem in karten_liste]

        def mein_filter2(nummer: int, andere_liste: list[int]):
            return [nummer + elem for elem in andere_liste]

        filter_liste = [
            KartenfilterTupel(mein_filter, {'nummer': 10}),
            KartenfilterTupel(mein_filter, {'nummer': 100}),
            KartenfilterTupel(mein_filter, {'nummer': 1000}),
        ]
        filter_liste2 = [
            KartenfilterTupel(mein_filter2, {'nummer': 10}, 'andere_liste'),
            KartenfilterTupel(mein_filter2, {'nummer': 100}, 'andere_liste'),
            KartenfilterTupel(mein_filter2, {'nummer': 1000}, 'andere_liste'),
        ]
        filter_liste3 = [
            KartenfilterTupel(mein_filter2, {'nummer': 10}, 'neue_liste'),
            KartenfilterTupel(mein_filter2, {'nummer': 100}, 'neue_liste'),
            KartenfilterTupel(mein_filter2, {'nummer': 1000}, 'neue_liste'),
        ]

        meine_liste = [1, 2, 3]
        self.assertEquals([1111, 1112, 1113],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste, liste=cast(list[Vokabelkarte],
                                                                                                    meine_liste)))
        self.assertEquals([1111, 1112, 1113],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste, liste=cast(list[Vokabelkarte],
                                                                                                    meine_liste)))
        self.assertEquals([],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste, liste=[]))
        self.assertEquals([1, 2, 3],
                          KartenfilterStrategie.filter_karten(filter_tupel=[], liste=cast(list[Vokabelkarte],
                                                                                          meine_liste)))
        self.assertEquals([], KartenfilterStrategie.filter_karten())
        self.assertEquals([],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste))
        self.assertEquals([1, 2, 3], KartenfilterStrategie.filter_karten(liste=cast(list[Vokabelkarte],
                                                                                    meine_liste)))
        self.assertEquals([], KartenfilterStrategie.filter_karten(cast(list[KartenfilterTupel], meine_liste)),
                          "Ohne Argumentnamen")
        self.assertEquals([1111, 1112, 1113],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste2,
                                                              liste=cast(list[Vokabelkarte],
                                                                         meine_liste)), "eigener arg_name")
        self.assertEquals([],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste3,
                                                              liste=cast(list[Vokabelkarte],
                                                                         meine_liste)), "Falscher arg_name")

    def test_filterkartenstatistik(self):
        result = FilterKartenstatistik(StatistikfilterNeue, self.obj.aktuelle_box(), 1000)
        self.assertEquals(30, len(result.filter(self.liste)))
        result = FilterKartenstatistik(StatistikfilterPruefen, self.obj.aktuelle_box(), 1000)
        self.assertEquals(0, len(result.filter(self.liste)))

    def test_filtervokabelbox(self):
        """siehe entsprechenden Test in test_vokabeltrainermodell.py"""
        pass

    def test_filterkartenanzahl(self):
        result = FilterKartenanzahl(max_anzahl=10)
        self.assertEqual(10, len(list(result.filter(self.liste))))
        result = FilterKartenanzahl()
        self.assertEqual(0, len(list(result.filter(self.liste))))
        result = FilterKartenanzahl()
        self.assertEqual(0, len(list(result.filter([]))))
        result = FilterKartenanzahl(max_anzahl=len(self.liste) + 10)
        self.assertEqual(len(self.liste), len(list(result.filter(self.liste))))

    def test_filtermischen(self):
        result = FilterMischen()
        self.assertNotEqual(self.liste, list(result.filter(self.liste)))
        self.assertEqual(self.liste[:1], list(result.filter(self.liste[:1])))
        self.assertEqual([], list(result.filter([])))
