from unittest import TestCase
from lerneinheit import LerneinheitStandard, LerneinheitJapanisch, LerneinheitFactory

class test_Lerneinheit(TestCase):

    def setUp(self):
        self.listeA = LerneinheitFactory.erzeuge_standard_beispiele(anzahl=10)
        self.listeB = LerneinheitFactory.erzeuge_standard_beispiele(anzahl=10)
        self.objA = LerneinheitStandard(self.listeA[1].eintrag,
                                        self.listeA[1].beschreibung,
                                        self.listeA[1].erzeugt,
                                        self.listeA[1].daten.update({"plus": 0}))
        objB = LerneinheitStandard(self.listeA[1].eintrag,
                                   self.listeA[1].beschreibung,
                                   self.listeA[1].erzeugt,
                                   self.listeA[1].daten)
        self.listeC = LerneinheitFactory.erzeuge_japanisch_beispiele(anzahl=10)
        self.listeC = LerneinheitFactory.erzeuge_japanisch_kanji_beispiele(anzahl=10)
        self.listeC = LerneinheitFactory.erzeuge_chinesisch_beispiele(anzahl=10)

    def test_erzeugen(self):
        self.assertEquals("", LerneinheitStandard().eintrag)
        self.assertEquals("", LerneinheitStandard().beschreibung)
        self.assertEquals(0, LerneinheitStandard().erzeugt)
        self.assertEquals({}, LerneinheitStandard().daten)

    def test_suche_meine_frageeinheiten(self):
        result = LerneinheitJapanisch.suche_meine_frageeinheiten()
        self.assertEquals(4, len(result))

    def test_gleiche_lerneinheit_wie(self):
        self.assertTrue(self.listeA[1].gleiche_lerneinheit_wie(self.listeB[1]),
                        "listeA[1] ist gleichLerneinheit wie listeB[1]")
        self.assertTrue(self.listeA[1].gleiche_lerneinheit_wie(self.objA),
                        "listeA[1] ist gleichLerneinheit wie objA")
        self.assertFalse(self.listeA[1].gleiche_lerneinheit_wie(self.listeA[2]),
                         "listeA[1] ist nicht gleichLerneinheit wie listeA[2]")

    def test_absolut_gleich_wie(self):
        self.assertFalse(self.listeA[1].absolut_gleich_wie(self.listeB[1]),
                         "listeA[1] ist nicht absolutGleichWie wie listeB[1]")
        self.assertTrue(self.listeA[1].absolut_gleich_wie(self.objA),
                        "listeA[1] ist absolutGleichWie wie objA")
        self.assertFalse(self.listeA[1].absolut_gleich_wie(self.listeA[2]),
                         "listeA[1] ist nicht absolutGleichWie wie listeA[2]")
        self.assertTrue(self.listeA[1].absolut_gleich_wie(self.objA),
                        "listeA[1] ist absolutGleichWie wie objA")
        self.assertTrue(self.objA.absolut_gleich_wie(self.objA),
                        "objA ist absolutGleichWie wie objB")