from unittest import TestCase
from src.classes.kartenfilter import KartenfilterTupel, FilterKartenstatistik, KartenfilterStrategie
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
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste, liste=meine_liste))
        self.assertEquals([1111, 1112, 1113],
                          KartenfilterStrategie.filter_karten(filter_liste, meine_liste))
        self.assertEquals([],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste, liste=[]))
        self.assertEquals([1, 2, 3],
                          KartenfilterStrategie.filter_karten(filter_tupel=[], liste=meine_liste))
        self.assertEquals([], KartenfilterStrategie.filter_karten())
        self.assertEquals([],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste))
        self.assertEquals([1, 2, 3], KartenfilterStrategie.filter_karten(liste=meine_liste))
        self.assertEquals([], KartenfilterStrategie.filter_karten(meine_liste))
        self.assertEquals([1111, 1112, 1113],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste2,
                                                              liste=meine_liste), "eigener arg_name")
        self.assertEquals([],
                          KartenfilterStrategie.filter_karten(filter_tupel=filter_liste3,
                                                              liste=meine_liste), "Falscher arg_name")

    def test_filterkartenstatistik(self):
        result = FilterKartenstatistik(StatistikfilterNeue, self.obj.aktuelle_box(), 1000)
        self.assertEquals(30, len(result.filter(self.liste)))
        result = FilterKartenstatistik(StatistikfilterPruefen, self.obj.aktuelle_box(), 1000)
        self.assertEquals(0, len(result.filter(self.liste)))

    def test_filtervokabelbox(self):
        pass
