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
from src.classes.statistikfilter import (StatistikfilterNeue, StatistikfilterPruefen, StatistikfilterNeueAlle,
                                         StatistikfilterLernenAlle)
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

    def test_filterliste_vokabeln_pruefen(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        filter_liste = self.komplett.filterliste_vokabeln_pruefen(
            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(5,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = self.komplett.filterliste_vokabeln_pruefen(
            zeit=Lernuhr.isostring_to_millis("2028-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(20,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = self.komplett.filterliste_vokabeln_pruefen(
            zeit=Lernuhr.isostring_to_millis("2023-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_lernen(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        filter_liste = self.komplett.filterliste_vokabeln_lernen(
            zeit=Lernuhr.isostring_to_millis("2024-07-12 03:00:00.000"),
            max_anzahl=20)
        self.assertEqual(16,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = self.komplett.filterliste_vokabeln_lernen(
            zeit=Lernuhr.isostring_to_millis("2028-08-12 13:00:00.000"),
            max_anzahl=2000)
        self.assertEqual(26,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = self.komplett.filterliste_vokabeln_lernen(
            zeit=Lernuhr.isostring_to_millis("2023-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_lernen_alle(self):
        # Teste, ob LernenAlle unabhaengig von der Zeit ist
        self.komplett = replace(self.komplett, index_aktuelle_box=72)
        print(f"\n {self.komplett.aktuelle_box().titel}")
        filter_liste = self.komplett.filterliste_genericstatistik(
            strategie=StatistikfilterLernenAlle,
            zeit=Lernuhr.isostring_to_millis("2024-06-12 03:00:00.000"),
            max_anzahl=20000)
        self.assertEqual(3,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        self.komplett = replace(self.komplett, index_aktuelle_box=72)
        print(f"\n {self.komplett.aktuelle_box().titel}")
        filter_liste = self.komplett.filterliste_genericstatistik(
            strategie=StatistikfilterLernenAlle,
            zeit=Lernuhr.isostring_to_millis("2024-08-12 03:00:00.000"),
            max_anzahl=20000)
        self.assertEqual(3,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        # Als Vergleich mit notmalen LernenFilter
        filter_liste = self.komplett.filterliste_vokabeln_lernen(
            zeit=Lernuhr.isostring_to_millis("2024-06-12 03:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = self.komplett.filterliste_vokabeln_lernen(
            zeit=Lernuhr.isostring_to_millis("2024-08-12 03:00:00.000"),
            max_anzahl=20)
        self.assertEqual(3,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_neue(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=0)    # Saetze
        filter_liste = self.komplett.filterliste_vokabeln_neue(
            zeit=Lernuhr.isostring_to_millis("2025-07-12 03:00:00.000"),
            max_anzahl=2000)
        self.assertEqual(170,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        # Neu auf die erste Frageeinheit angewendet ist unabhaengig von Zeit
        filter_liste = self.komplett.filterliste_vokabeln_neue(
            zeit=Lernuhr.isostring_to_millis("2024-06-12 03:00:00.000"),
            max_anzahl=2000)
        self.assertEqual(170,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        self.komplett = replace(self.komplett, index_aktuelle_box=40)  # Vokabeln der Lektion 3
        filter_liste = self.komplett.filterliste_vokabeln_neue(
            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_neue_mit_anderer_vokabelbox(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=0)    # Saetze
        aktuelle_box = self.komplett.aktuelle_box().naechste_frageeinheit()
        filter_liste = self.komplett.filterliste_vokabeln_neue(
            zeit=Lernuhr.isostring_to_millis("2025-07-12 03:00:00.000"),
            max_anzahl=2000,
            vokabelbox=aktuelle_box)
        self.assertEqual(204,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = self.komplett.filterliste_genericstatistik(
            strategie=StatistikfilterNeueAlle,
            zeit=Lernuhr.isostring_to_millis("2025-07-12 03:00:00.000"),
            max_anzahl=2000,
            vokabelbox=aktuelle_box)
        self.assertEqual(449,
                         len(list(
                             VokabeltrainerModell.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeltest_mit_teillisten(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        filter_liste = self.komplett.filterliste_vokabeln_pruefen(
            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"),
            max_anzahl=20)
        result = list(VokabeltrainerModell.filter_und_execute(funktion=lambda x: x,
                                                              filter_liste=filter_liste[:1],
                                                              liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        self.assertEqual(1789, len(result))
        result = list(VokabeltrainerModell.filter_und_execute(funktion=lambda x: x,
                                                              filter_liste=filter_liste[:2],
                                                              liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        self.assertEqual(1435, len(result))
        result = list(VokabeltrainerModell.filter_und_execute(funktion=lambda x: x,
                                                              filter_liste=filter_liste[:3],
                                                              liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        self.assertEqual(20, len(result))
        result = list(VokabeltrainerModell.filter_und_execute(funktion=None,
                                                              filter_liste=filter_liste[:2],
                                                              liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        result = list(VokabeltrainerModell.filter_und_execute(funktion=lambda x: x,
                                                              filter_liste=filter_liste[:3],
                                                              liste_der_vokabeln=cast(list[Vokabelkarte], result)))
        self.assertEqual(20, len(result))

    def test_filter_execute(self):
        def test_func(karte: Vokabelkarte) -> Vokabelkarte:
            return cast(Vokabelkarte, karte.lerneinheit.eintrag)
        result = VokabeltrainerModell.filter_und_execute(funktion=test_func,
                                                         filter_liste=[],
                                                         liste_der_vokabeln=self.liste)
        self.assertEqual([karte.lerneinheit.eintrag for karte, fun_result in result],
                         [fun_result for karte, fun_result in result])

    def test_datum_der_letzten_antwort(self):
        self.assertEqual(1720681644987, VokabeltrainerModell.datum_der_letzten_antwort())
        print(f"\n Datum: {datetime.fromtimestamp(1720681644987 / 1000).strftime('%F %T.%f')}")
