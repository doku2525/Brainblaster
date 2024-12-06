from unittest import TestCase
from src.classes.statistikmanager import StatistikManager, Frageeinheit
from src.classes.lerneinheit import LerneinheitChinesisch
from src.utils.utils_dataclass import mein_asdict


class test_statistikmanager(TestCase):

    def setUp(self):
        self.obj = StatistikManager.erzeuge(LerneinheitChinesisch)
        self.assertEquals({}, StatistikManager().statistiken)

    def test_fromdict(self):
        self.assertEqual(StatistikManager(),
                         StatistikManager.fromdict(mein_asdict(StatistikManager())))
        self.assertEqual(StatistikManager.erzeuge(LerneinheitChinesisch),
                         StatistikManager.fromdict(mein_asdict(StatistikManager.erzeuge(LerneinheitChinesisch))))

    def test_erzeuge(self):
        obj = StatistikManager.erzeuge(LerneinheitChinesisch)
        self.assertIs(type(obj), StatistikManager)
        self.assertEquals(len(obj.statistiken), 4)
        [self.assertTrue(issubclass(elem, Frageeinheit)) for elem in obj.statistiken.keys()]

    def test_liste_der_frageeinheiten(self):
        result = self.obj.liste_der_frageeinheiten()
        self.assertEquals(4, len(result))
        [self.assertEquals(index+1, elem().rank) for index, elem in enumerate(result)]

    def test_titel_der_frageeinheiten(self):
        result = self.obj.titel_der_frageeinheiten()
        self.assertEquals(4, len(result))

    # TODO Noch viele auskommentierte Tests
    # def test_ist_erste_frageeinheit(self):
    #     einheiten = self.obj.liste_der_frageeinheiten()
    #     self.assertTrue(self.obj.ist_erste_frageeinheit(einheiten[0]))
    #     self.assertFalse(self.obj.ist_erste_frageeinheit(einheiten[-1]))
    #     self.assertFalse(self.obj.ist_erste_frageeinheit(einheiten[1]))

    # def test_ist_letzte_frageeinheit(self):
    #     einheiten = self.obj.liste_der_frageeinheiten()
    #     self.assertTrue(self.obj.ist_letzte_frageeinheit(einheiten[-1]))
    #     self.assertTrue(self.obj.ist_letzte_frageeinheit(einheiten[3]))
    #     self.assertFalse(self.obj.ist_letzte_frageeinheit(einheiten[0]))
    #     self.assertFalse(self.obj.ist_letzte_frageeinheit(einheiten[1]))

    # def test_vorherige_frageeinheit(self):
    #     einheiten = self.obj.liste_der_frageeinheiten()
    #     self.assertEquals(einheiten[0], self.obj.vorherige_frageeinheit(einheiten[1]))
    #     self.assertEquals(einheiten[-1], self.obj.vorherige_frageeinheit(einheiten[0]))
    #     self.assertEquals(einheiten[-2], self.obj.vorherige_frageeinheit(einheiten[-1]))

    # def test_folgende_frageeinheit(self):
    #     einheiten = self.obj.liste_der_frageeinheiten()
    #     self.assertEquals(einheiten[0], self.obj.folgende_frageeinheit(einheiten[-1]))
    #     self.assertEquals(einheiten[0], self.obj.folgende_frageeinheit(einheiten[3]))
    #     self.assertEquals(einheiten[1], self.obj.folgende_frageeinheit(einheiten[0]))

    def test_suche_frageeinheit_nach_titel(self):
        titel_liste = self.obj.titel_der_frageeinheiten()
        for index, titel in enumerate(titel_liste):
            result = self.obj.suche_frageeinheit_nach_titel(titel)
            self.assertEquals(titel, result().titel())
            self.assertEquals(index+1, result().rank)

    def test_update_statistik_mit_antwort(self):
        from src.classes.antwort import Antwort
        from src.classes.statistik import Statistik

        frageeinheit = self.obj.liste_der_frageeinheiten()[0]
        objekt = self.obj.update_statistik_mit_antwort(frageeinheit, Antwort(6, 0))
        self.assertEqual(0, len(self.obj.statistiken[frageeinheit].antworten))
        self.assertEqual(1, len(objekt.statistiken[frageeinheit].antworten))
        self.assertIsInstance(objekt.statistiken[frageeinheit].antworten[0], Antwort)
        self.assertEqual('PRUEFEN', objekt.statistiken[frageeinheit].modus.name)
        self.assertEqual(6, objekt.statistiken[frageeinheit].antworten[0].antwort)
        # Fuege Antwort zur zweiten Freigeeinheit hinzu
        frageeinheit2 = self.obj.liste_der_frageeinheiten()[1]
        objekt = objekt.update_statistik_mit_antwort(frageeinheit2, Antwort(5, 0))
        self.assertEqual(0, len(self.obj.statistiken[frageeinheit2].antworten))
        self.assertEqual(1, len(objekt.statistiken[frageeinheit2].antworten))
        self.assertIsInstance(objekt.statistiken[frageeinheit2].antworten[0], Antwort)
        self.assertEqual('PRUEFEN', objekt.statistiken[frageeinheit2].modus.name)
        self.assertEqual(0, len(self.obj.statistiken[frageeinheit2].antworten))
        self.assertEqual(1, len(objekt.statistiken[frageeinheit2].antworten))
        self.assertIsInstance(objekt.statistiken[frageeinheit2].antworten[0], Antwort)
        self.assertEqual('PRUEFEN', objekt.statistiken[frageeinheit2].modus.name)
        self.assertEqual(5, objekt.statistiken[frageeinheit2].antworten[0].antwort)
        # Pruefe, ob die Veraenderung in der ersten Frageeinheit immer noch existieren
        self.assertEqual(0, len(self.obj.statistiken[frageeinheit].antworten))
        self.assertEqual(1, len(objekt.statistiken[frageeinheit].antworten))
        self.assertIsInstance(objekt.statistiken[frageeinheit].antworten[0], Antwort)
        self.assertEqual('PRUEFEN', objekt.statistiken[frageeinheit].modus.name)
        self.assertEqual(6, objekt.statistiken[frageeinheit].antworten[0].antwort)
