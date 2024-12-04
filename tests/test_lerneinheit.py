from unittest import TestCase
from src.classes.lerneinheit import (LerneinheitFactory, LerneinheitJapanisch, LerneinheitChinesisch,
                                     LerneinheitStandard, LerneinheitJapanischKanji)
from src.utils.utils_dataclass import mein_asdict


class test_Lerneinheit(TestCase):

    def setUp(self):
        self.listeA = LerneinheitFactory.erzeuge_standard_beispiele(anzahl=10)
        self.listeB = LerneinheitFactory.erzeuge_standard_beispiele(anzahl=10)
        self.objA = LerneinheitStandard(self.listeA[1].eintrag,
                                        self.listeA[1].beschreibung,
                                        self.listeA[1].erzeugt,
                                        self.listeA[1].daten | {"plus": 0})
        self.listeC = LerneinheitFactory.erzeuge_japanisch_beispiele(anzahl=10)
        self.listeD = LerneinheitFactory.erzeuge_japanisch_kanji_beispiele(anzahl=10)
        self.listeE = LerneinheitFactory.erzeuge_chinesisch_beispiele(anzahl=10)

    def test_fromdict_asdict(self):
        # TODO Funktioniert nur bei Objekten der gleichen Klasse. Ohne jegliche Fehlerkontrolle
        self.assertEqual(LerneinheitStandard(), LerneinheitStandard.fromdict(mein_asdict(LerneinheitStandard())))
        self.assertEqual(LerneinheitJapanisch(), LerneinheitJapanisch.fromdict(mein_asdict(LerneinheitJapanisch())))
        self.assertEqual(self.objA, self.objA.__class__.fromdict(mein_asdict(self.objA)))
        self.assertEqual(self.listeA[0], LerneinheitStandard.fromdict(mein_asdict(self.listeA[0])))
        self.assertEqual(self.listeB[0], LerneinheitStandard.fromdict(mein_asdict(self.listeB[0])))
        self.assertEqual(self.listeC[0], LerneinheitJapanisch.fromdict(mein_asdict(self.listeC[0])))
        self.assertEqual(self.listeD[0], LerneinheitJapanischKanji.fromdict(mein_asdict(self.listeD[0])))
        self.assertEqual(self.listeE[0], LerneinheitChinesisch.fromdict(mein_asdict(self.listeE[0])))

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
