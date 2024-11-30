from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from dataclasses import replace
from src.classes.vokabeltrainermodell import VokabeltrainerModell
from src.classes.kartenfilter import KartenfilterTupel, KartenfilterStrategie
from src.classes.vokabelkarte import Vokabelkarte
from src.classes.vokabelbox import Vokabelbox
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository
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

    def test_starte_vokabeltest(self):
        def test_func(karte: Vokabelkarte) -> Vokabelkarte:
            return karte.lerneinheit.eintrag

        with patch('src.classes.kartenfilter.KartenfilterStrategie.filter_karten') as mock_filter_karten:
            mock_filter_karten.return_value = self.liste
            result = self.obj.starte_vokabeltest(test_funktion=test_func, zeit=0)
            mock_filter_karten.assert_called_once()
            self.assertEquals(20, len(result))
            self.assertIsInstance(result[0][0], Vokabelkarte)
            self.assertIsInstance(result[0][1], str)
            self.assertNotEqual([karte.lerneinheit.eintrag for karte in self.liste],
                                [karte.lerneinheit.eintrag for karte, name in result], "Teste, ob Gemischt?")
            self.assertEqual([karte.lerneinheit.eintrag for karte, name in result],
                             [name for karte, name in result])

    def test_addVokabelkarte(self):
        pass
#        assert False
#        self.assertFalse(VokabeltrainerModell.vokabelkarten)
#        self.assertFalse(self.obj.vokabelboxen)
#        VokabeltrainerModell.addBeispiele(20, "Japanisch")
#        self.assertEquals(len(VokabeltrainerModell.vokabelkarten), 20)
#        self.assertFalse(self.obj.vokabelboxen)
#        VokabeltrainerModell.addBeispiele(80, "Chinesisch")
#        self.assertEquals(len(VokabeltrainerModell.vokabelkarten), 100)

    def test_speicherVokabelkartenInDatei(self):
        # TODO
        pass
#        VokabeltrainerModell.addBeispiele(5, "Japanisch")
#        VokabeltrainerModell.speicherVokabelkartenInDatei()
#        VokabeltrainerModell.speicherVokabelkartenInJSON()
