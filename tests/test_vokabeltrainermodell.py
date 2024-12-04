from unittest import TestCase
from unittest.mock import patch, MagicMock
from dataclasses import replace
from datetime import datetime, timedelta
from functools import reduce
from typing import cast

from src.classes.lernuhr import Lernuhr
from src.classes.vokabeltrainermodell import VokabeltrainerModell
from src.classes.kartenfilter import (KartenfilterTupel, KartenfilterStrategie, FilterKartenstatistik,
                                      FilterVokabelbox, FilterKartenanzahl, FilterMischen)
from src.classes.vokabelkarte import Vokabelkarte
from src.classes.vokabelbox import Vokabelbox
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, JSONDateiformatVokabelkarte
from src.classes.statistikfilter import StatistikfilterNeue, StatistikfilterPruefen
from src.classes.lerneinheit import LerneinheitChinesisch


class test_vokabeltrainermodell(TestCase):

    def setUp(self):
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
        self.assertEqual(0, self.komplett.index_aktuelle_box)
        self.assertEqual(83, len(self.komplett.vokabelboxen.vokabelboxen))
        self.assertEqual(3058, len(self.komplett.alle_vokabelkarten()))
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        self.assertEqual('Integrated Chinese Vokabeln Lektion 101', self.komplett.aktuelle_box().titel)

    def teste_kartenfilter_vokabelbox(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        mein_filter = FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box())
        self.assertEqual(40, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))
        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        mein_filter = FilterVokabelbox(vokabelbox=self.komplett.aktuelle_box())
        self.assertEqual(1789, len(list(mein_filter.filter(karten_liste=self.komplett.alle_vokabelkarten()))))

    def teste_kartenfilter_statistik(self):
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

    def test_starte_vokabeltest(self):
        def test_func(karte: Vokabelkarte) -> Vokabelkarte:
            return cast(Vokabelkarte, karte.lerneinheit.eintrag)

        with patch('src.classes.kartenfilter.KartenfilterStrategie.filter_karten') as mock_filter_karten:
            mock_filter_karten.return_value = self.liste
            result = self.obj.starte_vokabeltest(test_funktion=test_func, zeit=0)
            mock_filter_karten.assert_called_once()
            # Result = Liste aus Tupel(karte, f(karte)).
            self.assertEqual([karte.lerneinheit.eintrag for karte, fun_result in result],
                             [fun_result for karte, fun_result in result])

    def test_datum_der_letzten_antwort(self):
        self.assertEqual(1720681644987, VokabeltrainerModell.datum_der_letzten_antwort())
        print(f"\n Datum: {datetime.fromtimestamp(1720681644987 / 1000).strftime('%F %T.%f')}")
