from unittest import TestCase
from dataclasses import replace
from typing import cast

from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.kartenfilter import KartenfilterTupel

from src.classes.lernuhr import Lernuhr


class test_FilterlistenFactory(TestCase):

    def setUp(self):
        from src.classes.vokabeltrainermodell import VokabeltrainerModell
        from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
        from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, \
            JSONDateiformatVokabelkarte

        self.komplett = VokabeltrainerModell(
            vokabelkarten=InMemoryVokabelkartenRepository(dateiname='_vokabelkarten_2024.JSON',
                                                          verzeichnis='',
                                                          speicher_methode=JSONDateiformatVokabelkarte),
            vokabelboxen=InMemeoryVokabelboxRepository(dateiname='_vokabelboxen_2024.JSON',
                                                       speicher_methode=JSONDateiformatVokabelbox))
        self.komplett.vokabelkarten.laden()
        self.komplett.vokabelboxen.laden()

    def test_filterliste_genericstatistik(self):
        liste = FilterlistenFactory.filterliste_genericstatistik(None, 0, 0, 0)
        self.assertEqual(4, len(liste))
        for elem in liste:
            self.assertIsInstance(elem, KartenfilterTupel)

    def test_filterliste_vokabeln_pruefen(self):
        liste = FilterlistenFactory.filterliste_vokabeln_pruefen(None, 0, 0)
        self.assertEqual(4, len(liste))
        for elem in liste:
            self.assertIsInstance(elem, KartenfilterTupel)

    def test_filterliste_vokabeln_lernen(self):
        liste = FilterlistenFactory.filterliste_vokabeln_lernen(None, 0, 0)
        self.assertEqual(4, len(liste))
        for elem in liste:
            self.assertIsInstance(elem, KartenfilterTupel)

    def test_filterliste_vokabeln_neue(self):
        liste = FilterlistenFactory.filterliste_vokabeln_neue(None, 0, 0)
        self.assertEqual(4, len(liste))
        for elem in liste:
            self.assertIsInstance(elem, KartenfilterTupel)

    def test_filterliste_vokabeln_pruefen_mit_vokabeltrainer(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        filter_liste = FilterlistenFactory.filterliste_vokabeln_pruefen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(5,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = FilterlistenFactory.filterliste_vokabeln_pruefen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2028-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(20,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = FilterlistenFactory.filterliste_vokabeln_pruefen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2023-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_lernen_mit_vokabeltrainer(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        filter_liste = FilterlistenFactory.filterliste_vokabeln_lernen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-07-12 03:00:00.000"),
            max_anzahl=20)
        self.assertEqual(16,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = FilterlistenFactory.filterliste_vokabeln_lernen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2028-08-12 13:00:00.000"),
            max_anzahl=2000)
        self.assertEqual(26,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = FilterlistenFactory.filterliste_vokabeln_lernen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2023-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_lernen_alle_mit_vokabeltrainer(self):
        from src.classes.statistikfilter import StatistikfilterLernenAlle

        # Teste, ob LernenAlle unabhaengig von der Zeit ist
        self.komplett = replace(self.komplett, index_aktuelle_box=72)
        filter_liste = FilterlistenFactory.filterliste_genericstatistik(
            vokabelbox=self.komplett.aktuelle_box(),
            strategie=StatistikfilterLernenAlle,
            zeit=Lernuhr.isostring_to_millis("2024-06-12 03:00:00.000"),
            max_anzahl=20000)
        self.assertEqual(3,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        self.komplett = replace(self.komplett, index_aktuelle_box=72)
        print(f"\n {self.komplett.aktuelle_box().titel}")
        filter_liste = FilterlistenFactory.filterliste_genericstatistik(
            vokabelbox=self.komplett.aktuelle_box(),
            strategie=StatistikfilterLernenAlle,
            zeit=Lernuhr.isostring_to_millis("2024-08-12 03:00:00.000"),
            max_anzahl=20000)
        self.assertEqual(3,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        # Als Vergleich mit notmalen LernenFilter
        filter_liste = FilterlistenFactory.filterliste_vokabeln_lernen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-06-12 03:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = FilterlistenFactory.filterliste_vokabeln_lernen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-08-12 03:00:00.000"),
            max_anzahl=20)
        self.assertEqual(3,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_neue_mit_vokabeltrainer(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=0)    # Saetze
        filter_liste = FilterlistenFactory.filterliste_vokabeln_neue(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2025-07-12 03:00:00.000"),
            max_anzahl=2000)
        self.assertEqual(170,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        # Neu auf die erste Frageeinheit angewendet ist unabhaengig von Zeit
        filter_liste = FilterlistenFactory.filterliste_vokabeln_neue(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-06-12 03:00:00.000"),
            max_anzahl=2000)
        self.assertEqual(170,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        self.komplett = replace(self.komplett, index_aktuelle_box=40)  # Vokabeln der Lektion 3
        filter_liste = FilterlistenFactory.filterliste_vokabeln_neue(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"),
            max_anzahl=20)
        self.assertEqual(0,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeln_neue_mit_anderer_vokabelbox_vokabeltrainer(self):
        from src.classes.statistikfilter import StatistikfilterNeueAlle

        self.komplett = replace(self.komplett, index_aktuelle_box=0)    # Saetze
        aktuelle_box = self.komplett.aktuelle_box().naechste_frageeinheit()
        filter_liste = FilterlistenFactory.filterliste_vokabeln_neue(
            zeit=Lernuhr.isostring_to_millis("2025-07-12 03:00:00.000"),
            max_anzahl=2000,
            vokabelbox=aktuelle_box)
        self.assertEqual(204,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )
        filter_liste = FilterlistenFactory.filterliste_genericstatistik(
            strategie=StatistikfilterNeueAlle,
            zeit=Lernuhr.isostring_to_millis("2025-07-12 03:00:00.000"),
            max_anzahl=2000,
            vokabelbox=aktuelle_box)
        self.assertEqual(449,
                         len(list(
                             FilterlistenFactory.filter_und_execute(
                                 funktion=lambda x: x,
                                 filter_liste=filter_liste,
                                 liste_der_vokabeln=self.komplett.alle_vokabelkarten())))
                         )

    def test_filterliste_vokabeltest_mit_teillisten_vokabeltrainer(self):
        from src.classes.vokabelkarte import Vokabelkarte

        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        filter_liste = FilterlistenFactory.filterliste_vokabeln_pruefen(
            vokabelbox=self.komplett.aktuelle_box(),
            zeit=Lernuhr.isostring_to_millis("2024-08-12 13:00:00.000"),
            max_anzahl=20)
        result = list(FilterlistenFactory.filter_und_execute(funktion=lambda x: x,
                                                             filter_liste=filter_liste[:1],
                                                             liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        self.assertEqual(1789, len(result))
        result = list(FilterlistenFactory.filter_und_execute(funktion=lambda x: x,
                                                             filter_liste=filter_liste[:2],
                                                             liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        self.assertEqual(1435, len(result))
        result = list(FilterlistenFactory.filter_und_execute(funktion=lambda x: x,
                                                             filter_liste=filter_liste[:3],
                                                             liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        self.assertEqual(20, len(result))
        result = list(FilterlistenFactory.filter_und_execute(funktion=None,
                                                             filter_liste=filter_liste[:2],
                                                             liste_der_vokabeln=self.komplett.alle_vokabelkarten()))
        result = list(FilterlistenFactory.filter_und_execute(funktion=lambda x: x,
                                                             filter_liste=filter_liste[:3],
                                                             liste_der_vokabeln=cast(list[Vokabelkarte], result)))
        self.assertEqual(20, len(result))

    def test_filter_execute(self):
        from src.classes.vokabelkarte import Vokabelkarte

        def test_func(karte: Vokabelkarte) -> Vokabelkarte:
            return cast(Vokabelkarte, karte.lerneinheit.eintrag)

        liste = Vokabelkarte.lieferBeispielKarten(30, 'LerneinheitChinesisch')
        # Mit Funktion != None => Liste aus Tupeln
        result = FilterlistenFactory.filter_und_execute(funktion=test_func,
                                                        filter_liste=[],
                                                        liste_der_vokabeln=liste)
        self.assertEqual([karte.lerneinheit.eintrag for karte, fun_result in result],
                         [fun_result for karte, fun_result in result])
        for elem in result:
            self.assertIsInstance(elem, tuple)
        # Mit Funktion != None => Liste aus Tupeln
        result = FilterlistenFactory.filter_und_execute(funktion=None,
                                                        filter_liste=[],
                                                        liste_der_vokabeln=liste)
        self.assertEqual(liste, result)
        for elem in result:
            self.assertIsInstance(elem, Vokabelkarte)
