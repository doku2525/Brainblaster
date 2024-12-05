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
