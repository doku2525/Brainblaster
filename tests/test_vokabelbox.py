from unittest import TestCase

import lerneinheit
from vokabelbox import Vokabelbox
from vokabelkarte import Vokabelkarte

class test_vokabelbox(TestCase):

    def setUp(self):
        self.kartenListe = Vokabelkarte.lieferBeispielKarten(100, "Chinesisch")
        self.kartenListe += Vokabelkarte.lieferBeispielKarten(200, "Japanisch")
        self.japBox = Vokabelbox('Japanisch', self.kartenListe[-1].lerneinheit.__class__, [])
        self.chiBox = Vokabelbox('Chinesisch', self.kartenListe[0].lerneinheit.__class__, [])
        self.assertEquals(300, len(self.kartenListe))

    def test_kleinerAls(self):
        self.assertLess(self.chiBox, self.japBox)
        liste = [self.japBox, self.chiBox]
        self.assertLess(liste[-1], liste[0])
        sortiert = sorted(liste)
        self.assertLess(sortiert[0], sortiert[-1])

    def test_renameBox(self):
        neuerName = "JLPT1"
        neueBox = self.japBox.rename(neuerName)
        self.assertEquals(neuerName, neueBox.titel)
        self.assertLess(neueBox, self.japBox)

    def test_verfuegbareFrageeinheiten(self):
        result = self.japBox.verfuegbare_frageeinheiten()
        self.assertEquals(4, len(result))
        self.assertEquals("JapanischBedeutung", result[0]().titel())
        objA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [])
        objB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], result[-1])
        self.assertEquals(objA.aktuelleFrage().titel(), "JapanischBedeutung")
        self.assertEquals(objB.aktuelleFrage().titel(), "JapanischSchreiben")

    # def test_ist_erste_frageeinheit(self):
    #     einheiten = frageeinheit.Frageeinheit.suche_frageeinheiten_der_lernklasse(lerneinheit.LerneinheitJapanisch)
    #     objA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [])
    #     objAA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[1])
    #     objB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[-1])
    #     objBB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[3])
    #     self.assertTrue(objA.ist_erste_frageeinheit())
    #     self.assertFalse(objAA.ist_erste_frageeinheit())
    #     self.assertFalse(objB.ist_erste_frageeinheit())
    #     self.assertFalse(objBB.ist_erste_frageeinheit())

    # def test_ist_letzte_frageeinheit(self):
    #     einheiten = frageeinheit.Frageeinheit.suche_frageeinheiten_der_lernklasse(lerneinheit.LerneinheitJapanisch)
    #     objA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [])
    #     objAA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[1])
    #     objB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[-1])
    #     objBB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[3])
    #     self.assertFalse(objA.ist_letzte_frageeinheit())
    #     self.assertFalse(objAA.ist_letzte_frageeinheit())
    #     self.assertTrue(objB.ist_letzte_frageeinheit())
    #     self.assertTrue(objBB.ist_letzte_frageeinheit())

    # def test_naechsteFrageeinheit(self):
    #     einheiten = frageeinheit.Frageeinheit.suche_frageeinheiten_der_lernklasse(lerneinheit.LerneinheitJapanisch)
    #     objA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [])
    #     objAA = objA.naechste_frageeinheit()
    #     objB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[-1])
    #     objBB = objB.naechste_frageeinheit()
    #     self.assertEquals(einheiten[0], objA.aktuelleFrage)
    #     self.assertEquals(einheiten[-1], objB.aktuelleFrage)
    #     self.assertEquals(einheiten[1], objAA.aktuelleFrage)
    #     self.assertEquals(einheiten[0], objBB.aktuelleFrage)

    # def test_vorherigeFrageeinheit(self):
    #     einheiten = frageeinheit.Frageeinheit.suche_frageeinheiten_der_lernklasse(lerneinheit.LerneinheitJapanisch)
    #     objA = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [])
    #     objAA = objA.vorherige_frageeinheit()
    #     objB = Vokabelbox('Test', lerneinheit.LerneinheitJapanisch, [], einheiten[-1])
    #     objBB = objB.vorherige_frageeinheit()
    #     self.assertEquals(einheiten[0], objA.aktuelleFrage)
    #     self.assertEquals(einheiten[-1], objB.aktuelleFrage)
    #     self.assertEquals(einheiten[-1], objAA.aktuelleFrage)
    #     self.assertEquals(einheiten[2], objBB.aktuelleFrage)
    #     self.assertEquals(einheiten[-2], objBB.aktuelleFrage)

    def test_filterVokabelkarten(self):
        result = self.japBox.filter_vokabelkarten(self.kartenListe)
        self.assertEquals(200, len(result))
        result = self.chiBox.filter_vokabelkarten(self.kartenListe)
        self.assertEquals(100, len(result))
        hsk = []
        for i,elem in enumerate(result):
            if i < 30: elem.lerneinheit.daten["HSK"] = 1
            hsk.append(elem)
        self.assertEquals(len(hsk), len(result))
        fun = "('HSK',1) in a.lerneinheit.daten.items()"
        hskBox = Vokabelbox("HSK 1", self.chiBox.lernklasse, [fun])
        hskresult = hskBox.filter_vokabelkarten(self.kartenListe)
        self.assertEquals(len(list(hskresult)), 30)

    def test_mischeKarten(self):
        liste = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        result = Vokabelbox.mische_karten(liste)
        self.assertNotEqual(liste, result)
        self.assertEquals(liste, sorted(result))
