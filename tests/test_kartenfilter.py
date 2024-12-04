from unittest import TestCase
from dataclasses import replace
from typing import cast
from src.classes.kartenfilter import (KartenfilterTupel, FilterKartenstatistik, KartenfilterStrategie, FilterMischen,
                                      FilterKartenanzahl, FilterVokabelbox)
from src.classes.lernuhr import Lernuhr


class test_Kartenfilter(TestCase):

    def setUp(self):
        from src.classes.vokabelbox import Vokabelbox
        from src.classes.vokabelkarte import Vokabelkarte
        from src.classes.vokabeltrainermodell import VokabeltrainerModell
        from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
        from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, \
            JSONDateiformatVokabelkarte

        self.liste = Vokabelkarte.lieferBeispielKarten(30, 'LerneinheitChinesisch')
        box = Vokabelbox('Chinesisch', self.liste[0].lerneinheit.__class__, [])
        self.obj = VokabeltrainerModell(vokabelkarten=InMemoryVokabelkartenRepository(dateiname='', verzeichnis=''),
                                        vokabelboxen=InMemeoryVokabelboxRepository())
        self.obj.vokabelboxen.vokabelboxen = [box]*3
        self.obj.vokabelkarten.vokabelkarten = [self.liste]
        # Lade kompletten Vokabeltrainer
        self.komplett = VokabeltrainerModell(
            vokabelkarten=InMemoryVokabelkartenRepository(dateiname='_vokabelkarten_2024.JSON',
                                                          verzeichnis='',
                                                          speicher_methode=JSONDateiformatVokabelkarte),
            vokabelboxen=InMemeoryVokabelboxRepository(dateiname='_vokabelboxen_2024.JSON',
                                                       speicher_methode=JSONDateiformatVokabelbox))
        self.komplett.vokabelkarten.laden()
        self.komplett.vokabelboxen.laden()

    def test_gefilterte_karten(self):
        from src.classes.vokabelkarte import Vokabelkarte

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
        from src.classes.statistikfilter import StatistikfilterNeue, StatistikfilterPruefen

        result = FilterKartenstatistik(StatistikfilterNeue, self.obj.aktuelle_box(), 1000)
        self.assertEquals(30, len(result.filter(self.liste)))
        result = FilterKartenstatistik(StatistikfilterPruefen, self.obj.aktuelle_box(), 1000)
        self.assertEquals(0, len(result.filter(self.liste)))

    def test_filtervokabelbox(self):
        """siehe entsprechenden Test unten teste_kartenfilter_vokabelbox_vokabeltrainer()"""
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

    def teste_kartenfilter_vokabelbox_vokabeltrainer(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_filter = FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box())
        self.assertEqual(40, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        mein_filter = FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box())
        self.assertEqual(1789, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))

    def teste_kartenfilter_statistik(self):
        from src.classes.statistikfilter import StatistikfilterPruefen

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_filter = FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                            vokabelbox=self.komplett.aktuelle_box(),
                                            zeit=Lernuhr.isostring_to_millis("2024-07-02 13:00:00.000"))
        self.assertEqual(0, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        mein_filter = FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                            vokabelbox=self.komplett.aktuelle_box(),
                                            zeit=Lernuhr.isostring_to_millis("2024-07-12 13:00:00.000"))
        self.assertEqual(291, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        mein_filter = FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                            vokabelbox=self.komplett.aktuelle_box(),
                                            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"))
        self.assertEqual(2514, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))

    def teste_kartenfilter_kartenzahl(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_filter = FilterKartenanzahl(max_anzahl=10)
        self.assertEqual(10, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        mein_filter = FilterKartenanzahl()
        self.assertEqual(0, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))

    def teste_kartenfilter_mischen(self):
        from functools import reduce

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_filter = FilterKartenanzahl(max_anzahl=10)
        result_normal = list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))
        mischen_filter = FilterMischen()
        result_gemischt = list(mischen_filter.filter(result_normal))
        self.assertEqual(10, len(result_gemischt))
        self.assertNotEqual(result_normal, result_gemischt)
        self.assertFalse(reduce(lambda result, neuer_wert: result and neuer_wert[0] == neuer_wert[1],
                                zip(result_normal, result_gemischt), True))
        for karte in result_normal:
            self.assertIn(karte, result_gemischt)

    def teste_kartenfilter_kombiniert(self):
        from src.classes.statistikfilter import StatistikfilterPruefen

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_box_filter = FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box())
        mein_filter = FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                            vokabelbox=self.komplett.aktuelle_box(),
                                            zeit=Lernuhr.isostring_to_millis("2024-07-02 13:00:00.000"))
        self.assertEqual(0,
                         len(list(
                             mein_filter.filter(
                                 karten_liste=mein_box_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))
                         )))
        mein_filter = FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                            vokabelbox=self.komplett.aktuelle_box(),
                                            zeit=Lernuhr.isostring_to_millis("2024-07-12 13:00:00.000"))
        self.assertEqual(0,
                         len(list(
                             mein_filter.filter(
                                 karten_liste=mein_box_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))
                         )))
        mein_filter = FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                            vokabelbox=self.komplett.aktuelle_box(),
                                            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"))
        self.assertEqual(5,
                         len(list(
                             mein_filter.filter(
                                 karten_liste=mein_box_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))
                         )))

    def teste_kartenfilter_tupel(self):
        from src.classes.statistikfilter import StatistikfilterPruefen

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_tupel = KartenfilterTupel(
            funktion=FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                           vokabelbox=self.komplett.aktuelle_box(),
                                           zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000")))
        self.assertEqual(2514,
                         len(list(mein_tupel.funktion.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        mein_box_tupel = KartenfilterTupel(funktion=FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box()))
        self.assertEqual(40,
                         len(list(mein_box_tupel.funktion.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        self.assertEqual(5,
                         len(list(
                             mein_box_tupel.funktion.filter(
                                 karten_liste=mein_tupel.funktion.filter(
                                     karten_liste=self.komplett.alle_vokabelkarten())
                             )
                         )))

    def teste_kartenfilterstatistik_filter_karten(self):
        from src.classes.statistikfilter import StatistikfilterPruefen

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_tupel = KartenfilterTupel(
            funktion=FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                           vokabelbox=self.komplett.aktuelle_box(),
                                           zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000")).filter,
            args={},
            arg_name_liste='karten_liste')
        mein_box_tupel = KartenfilterTupel(funktion=FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box()).filter)
        self.assertEqual(5,
                         len(list(
                             KartenfilterStrategie.filter_karten([mein_box_tupel, mein_tupel],
                                                                 self.komplett.alle_vokabelkarten())
                         )))
