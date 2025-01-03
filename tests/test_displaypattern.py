from unittest import TestCase
from src.classes.displaypattern import DisplayPatternVokabelkarte


class test_DisplayPattern(TestCase):

    def setUp(self):
        from src.classes.vokabeltrainermodell import VokabeltrainerModell
        from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
        from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, \
            JSONDateiformatVokabelkarte

        komplett = VokabeltrainerModell(
            vokabelkarten=InMemoryVokabelkartenRepository(dateiname='_vokabelkarten_2024.JSON',
                                                          verzeichnis='',
                                                          speicher_methode=JSONDateiformatVokabelkarte),
            vokabelboxen=InMemeoryVokabelboxRepository(dateiname='_vokabelboxen_2024.JSON',
                                                       speicher_methode=JSONDateiformatVokabelbox))
        komplett.vokabelkarten.laden()
        komplett.vokabelboxen.laden()
        self.karte = komplett.vokabelkarten.vokabelkarten[0]

        from src.classes.vokabelkarte import Vokabelkarte
        self.karte_jap = Vokabelkarte.lieferBeispielKarten(1, "Japanisch")
        self.karte_kanji = Vokabelkarte.lieferBeispielKarten(1, "Kanji")
        self.karte_chn = Vokabelkarte.lieferBeispielKarten(1, "Chinesisch")

    def test_in_vokabel_liste(self):
        objekt = DisplayPatternVokabelkarte.in_vokabel_liste(self.karte_jap[0])
        self.assertEqual(3, len(objekt.lerneinheit))
        self.assertEqual({}, objekt.statistiken)
        objekt = DisplayPatternVokabelkarte.in_vokabel_liste(self.karte_chn[0])
        self.assertEqual(4, len(objekt.lerneinheit))
        self.assertEqual({}, objekt.statistiken)
        objekt = DisplayPatternVokabelkarte.in_vokabel_liste(self.karte_kanji[0])
        self.assertEqual(4, len(objekt.lerneinheit))
        self.assertEqual({}, objekt.statistiken)
        objekt = DisplayPatternVokabelkarte.in_vokabel_liste(self.karte)
        self.assertEqual(4, len(objekt.lerneinheit))
        self.assertNotEqual({}, objekt.statistiken)

    def test_display_statistik(self):
        result = DisplayPatternVokabelkarte.display_statistik(self.karte)
        expected = {'ChinesischBedeutung': {'ef': '4.10',
                                            'folge': '6 6 6 6 6',
                                            'last': '24-07-09 00:02',
                                            'next': '24-08-19 00:02'},
                    'ChinesischEintrag': {'ef': '3.94',
                                          'folge': '6 6 6 6 6',
                                          'last': '24-06-06 19:39',
                                          'next': '24-07-12 06:42'},
                    'ChinesischPinyin': {'ef': '4.10',
                                         'folge': '6 6 6 6 6',
                                         'last': '24-07-09 00:04',
                                         'next': '24-08-19 00:04'},
                    'ChinesischSchreiben': {'ef': '3.88',
                                            'folge': '6 6 6 6 6',
                                            'last': '24-06-23 18:20',
                                            'next': '24-07-28 16:25'}}
        self.assertEqual(expected, result)
