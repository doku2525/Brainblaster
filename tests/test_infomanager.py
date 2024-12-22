from unittest import TestCase

from src.classes.infomanager import InfoManager
from src.classes.lerninfos import Lerninfos


class test_InfoManager(TestCase):

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

    def test_factory(self):
        objekt = InfoManager.factory(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
                                     liste_der_karten=self.komplett.alle_vokabelkarten())
        self.assertIsInstance(objekt, InfoManager)
        self.assertEqual(len(self.komplett.vokabelboxen.vokabelboxen), len(objekt.boxen))
        self.assertIsInstance(objekt.boxen[0], Lerninfos)
        self.assertEqual(self.komplett.vokabelboxen.titel_aller_vokabelboxen(),
                         [linfo.box.titel for linfo in objekt.boxen])
        self.assertEqual(40, objekt.boxen[40].gesamtzahl)
        self.assertEqual(1789, objekt.boxen[80].gesamtzahl)
        self.assertEqual(942, objekt.boxen[81].gesamtzahl)
        self.assertEqual({}, objekt.boxen[80].infos)

    def test_erzeuge_alle_infos(self):
        from src.classes.lernuhr import Lernuhr

        objekt = (InfoManager.factory(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
                                      liste_der_karten=self.komplett.alle_vokabelkarten()).
                  erzeuge_alle_infos(Lernuhr.isostring_to_millis("2024-07-12 13:00:00.000")))
        self.assertNotEqual({}, objekt.boxen[80].infos)

    def test_suche_karte(self):
        objekt = InfoManager.factory(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
                                     liste_der_karten=self.komplett.alle_vokabelkarten())
        karte = objekt.boxen[40].karten[0]  # Eintrag = '你'
        self.assertEquals(karte, objekt.boxen[40].karten[0])
        self.assertIn(karte, objekt.boxen[40].karten)
        self.assertIsInstance(objekt.suche_karte(karte), list)
        self.assertEqual(3, len(objekt.suche_karte(karte)))
        self.assertEqual([objekt.boxen[40], objekt.boxen[80], objekt.boxen[81]], objekt.suche_karte(karte))

    def test_werte_als_dictionary(self):
        from src.classes.lernuhr import Lernuhr
        from src.classes.frageeinheit import FrageeinheitChinesischBedeutung, FrageeinheitChinesischPinyin

        objekt = InfoManager.factory(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
                                     liste_der_karten=self.komplett.alle_vokabelkarten())
        objekt = objekt.erzeuge_alle_infos(Lernuhr.isostring_to_millis("2024-07-12 13:00:00.000"))
        expected_bed = {'pruefen': {'insgesamt': 1763, 'aktuell': 205},
                    'lernen': {'insgesamt': 26, 'aktuell': 20},
                    'neu': {'insgesamt': 0, 'aktuell': 0}}
        expected_pin = {'pruefen': {'aktuell': 205, 'insgesamt': 1423},
                    'lernen': {'aktuell': 19, 'insgesamt': 29},
                    'neu': {'aktuell': 290, 'insgesamt': 337}}
        self.assertEqual(expected_bed, objekt.boxen[80].infos[FrageeinheitChinesischBedeutung].as_number_dict())
        self.assertEqual(expected_pin, objekt.boxen[80].infos[FrageeinheitChinesischPinyin].as_number_dict())

    def test_boxen_als_number_dict(self):
        from src.classes.lernuhr import Lernuhr
        from src.classes.frageeinheit import FrageeinheitChinesischBedeutung, FrageeinheitChinesischPinyin

        objekt = InfoManager.factory(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
                                     liste_der_karten=self.komplett.alle_vokabelkarten())
        objekt = objekt.erzeuge_alle_infos(Lernuhr.isostring_to_millis("2024-07-12 13:00:00.000"))
        expected_bed = {'pruefen': {'insgesamt': 1763, 'aktuell': 205},
                        'lernen': {'insgesamt': 26, 'aktuell': 20},
                        'neu': {'insgesamt': 0, 'aktuell': 0}}
        expected_pin = {'pruefen': {'aktuell': 205, 'insgesamt': 1423},
                        'lernen': {'aktuell': 19, 'insgesamt': 29},
                        'neu': {'aktuell': 290, 'insgesamt': 337}}
        result = objekt.boxen_als_number_dict()
        self.assertIsInstance(result, list)
        self.assertEqual(len(objekt.boxen), len(result))
        self.assertEqual(4, len(list(result[0].keys())))
        self.assertEqual(expected_bed, result[80]['FrageeinheitChinesischBedeutung'])
        self.assertEqual(expected_pin, result[80]['FrageeinheitChinesischPinyin'])

    # def test_factory_timings(self):
    #     import timeit
    #
    #     ausfuehrungszeit_ohne_multi = timeit.timeit(
    #         lambda: InfoManager.factory(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
    #                                     liste_der_karten=self.komplett.alle_vokabelkarten()),
    #         number=1)
    #     ausfuehrungszeit_mit_multi = timeit.timeit(
    #         lambda: InfoManager.factory_multiprocessing(liste_der_boxen=self.komplett.vokabelboxen.vokabelboxen,
    #                                                     liste_der_karten=self.komplett.alle_vokabelkarten()),
    #         number=1)
    #     print(f"\n Ohne: {ausfuehrungszeit_ohne_multi} Mit: {ausfuehrungszeit_mit_multi}")
    #     self.assertLess(ausfuehrungszeit_mit_multi, ausfuehrungszeit_ohne_multi)
