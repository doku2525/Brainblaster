from unittest import TestCase
from dataclasses import replace

from src.classes.lerninfos import Lerninfos
from src.classes.kartenfilter import FilterVokabelbox


class test_Lerninfos(TestCase):

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

    def test_gesamtzahl(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        self.assertEqual(40, objekt.gesamtzahl)

    def test_erzeuge_info_dict_lektion_1(self):
        from src.classes.lernuhr import Lernuhr
        from src.classes.frageeinheit import FrageeinheitChinesischBedeutung, Frageeinheit

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        objekt = (Lerninfos(
            box=self.komplett.aktuelle_box(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten())).
                  erzeuge_info_dict(Lernuhr.isostring_to_millis("2024-06-22 13:00:00.000")))
        self.assertIsInstance(objekt, Lerninfos)
        self.assertIsInstance(objekt.infos, dict)
        self.assertTrue(issubclass(list(objekt.infos.keys())[0], Frageeinheit))
        self.assertIn(FrageeinheitChinesischBedeutung, objekt.infos.keys())

    def test_sammle_infos_lektion_1(self):
        from src.classes.lernuhr import Lernuhr
        from src.classes.lerninfos import InfotypStatModus

        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-06-22 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(40, len(result[0].insgesamt))
        self.assertEqual(0, len(result[0].aktuell))
        self.assertEqual(0, len(result[1].insgesamt))
        self.assertEqual(0, len(result[1].aktuell))
        self.assertEqual(0, len(result[2].insgesamt))
        self.assertEqual(0, len(result[2].aktuell))
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2025-06-22 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(40, len(result[0].insgesamt))
        self.assertEqual(40, len(result[0].aktuell))
        self.assertEqual(0, len(result[1].insgesamt))
        self.assertEqual(0, len(result[1].aktuell))
        self.assertEqual(0, len(result[2].insgesamt))
        self.assertEqual(0, len(result[2].aktuell))

    def test_sammle_infos_alle_vokabeln_letzte_frageeinheit(self):
        from src.classes.lernuhr import Lernuhr
        from src.classes.lerninfos import InfotypStatModus

        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box().vorherige_frageeinheit(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-06-22 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(1789, sum([len(info.insgesamt) for info in result]))
        self.assertEqual(938, len(result[0].insgesamt))
        self.assertEqual(0, len(result[0].aktuell))
        self.assertEqual(21, len(result[1].insgesamt))
        self.assertEqual(0, len(result[1].aktuell))
        self.assertEqual(830, len(result[2].insgesamt))
        self.assertEqual(9, len(result[2].aktuell))
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box().vorherige_frageeinheit(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-07-12 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(1789, sum([len(info.insgesamt) for info in result]))
        self.assertEqual(938, len(result[0].insgesamt))
        self.assertEqual(50, len(result[0].aktuell))
        self.assertEqual(21, len(result[1].insgesamt))
        self.assertEqual(14, len(result[1].aktuell))
        self.assertEqual(830, len(result[2].insgesamt))
        self.assertEqual(80, len(result[2].aktuell))
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box().vorherige_frageeinheit(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-12-30 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(1789, sum([len(info.insgesamt) for info in result]))
        self.assertEqual(938, len(result[0].insgesamt))
        self.assertEqual(938, len(result[0].aktuell))
        self.assertEqual(21, len(result[1].insgesamt))
        self.assertEqual(21, len(result[1].aktuell))
        self.assertEqual(830, len(result[2].insgesamt))
        self.assertEqual(80, len(result[2].aktuell))

    def test_sammle_infos_alle_vokabeln_zweite_frageeinheit(self):
        from src.classes.lernuhr import Lernuhr
        from src.classes.lerninfos import InfotypStatModus

        self.komplett = replace(self.komplett, index_aktuelle_box=80)
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box().naechste_frageeinheit(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-06-22 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(1789, sum([len(info.insgesamt) for info in result]))
        self.assertEqual(1423, len(result[0].insgesamt))
        self.assertEqual(0, len(result[0].aktuell))
        self.assertEqual(29, len(result[1].insgesamt))
        self.assertEqual(0, len(result[1].aktuell))
        self.assertEqual(337, len(result[2].insgesamt))
        self.assertEqual(59, len(result[2].aktuell))
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box().naechste_frageeinheit(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-07-11 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(1789, sum([len(info.insgesamt) for info in result]))
        self.assertEqual(1423, len(result[0].insgesamt))
        self.assertEqual(77, len(result[0].aktuell))
        self.assertEqual(29, len(result[1].insgesamt))
        self.assertEqual(9, len(result[1].aktuell))
        self.assertEqual(337, len(result[2].insgesamt))
        self.assertEqual(290, len(result[2].aktuell))
        objekt = Lerninfos(
            box=self.komplett.aktuelle_box().naechste_frageeinheit(),
            karten=FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten()))
        result = objekt.sammle_infos(Lernuhr.isostring_to_millis("2024-12-30 13:00:00.000"))
        self.assertEqual(3, len(result))
        for index in range(3):
            self.assertIsInstance(result[index], InfotypStatModus)
        self.assertEqual(1789, sum([len(info.insgesamt) for info in result]))
        self.assertEqual(1423, len(result[0].insgesamt))
        self.assertEqual(1423, len(result[0].aktuell))
        self.assertEqual(29, len(result[1].insgesamt))
        self.assertEqual(29, len(result[1].aktuell))
        self.assertEqual(337, len(result[2].insgesamt))
        self.assertEqual(290, len(result[2].aktuell))

    def test_split_vokabelliste_by_status(self):
        self.komplett = replace(self.komplett, index_aktuelle_box=40)
        vokabelliste = FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten())
        result = Lerninfos.split_vokabelliste_by_status(
            vokabelliste,
            self.komplett.aktuelle_box().aktuelle_frage)
        self.assertEqual((40, 0, 0), (len(result[0]), len(result[1]), len(result[2])))

        self.komplett = replace(self.komplett, index_aktuelle_box=81)
        vokabelliste = FilterVokabelbox(self.komplett.aktuelle_box()).filter(self.komplett.alle_vokabelkarten())
        result = Lerninfos.split_vokabelliste_by_status(
            vokabelliste,
            self.komplett.aktuelle_box().aktuelle_frage)
        self.assertEqual((942, 0, 0), (len(result[0]), len(result[1]), len(result[2])))
        result = Lerninfos.split_vokabelliste_by_status(
            vokabelliste,
            self.komplett.aktuelle_box().vorherige_frageeinheit().aktuelle_frage)
        self.assertEqual((907, 20, 15), (len(result[0]), len(result[1]), len(result[2])))
        self.assertEqual(942, sum((len(result[0]), len(result[1]), len(result[2]))))
