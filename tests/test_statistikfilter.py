from unittest import TestCase
from src.classes.statistikfilter import (StatistikfilterPruefen, StatistikfilterNeue,
                                         StatistikfilterLernen, StatistikfilterLernenAlle)
from src.classes.statistikmanager import StatistikManager
from src.classes.frageeinheit import (FrageeinheitChinesischBedeutung, FrageeinheitChinesischPinyin,
                                      FrageeinheitChinesischEintrag)


class test_Statistikfilter(TestCase):

    def setUp(self):
        self.stat_manager = StatistikManager.fromdict(
            {"statistiken": {"FrageeinheitChinesischBedeutung": {
                    "modus": "PRUEFEN", "antworten": [{"antwort": 6, "erzeugt": 0}]},
             "FrageeinheitChinesischPinyin": {
                    "modus": "LERNEN", "antworten": [{"antwort": 2, "erzeugt": 0}]},
             "FrageeinheitChinesischEintrag": {
                    "modus": "NEU", "antworten": []}}
             })
        self.stat_manager2 = StatistikManager.fromdict(
            {"statistiken": {"FrageeinheitChinesischBedeutung": {
                    "modus": "PRUEFEN", "antworten": [{"antwort": 6, "erzeugt": 10}]*4},
             "FrageeinheitChinesischPinyin": {
                    "modus": "NEU", "antworten": []}}
             })
        self.stat_manager3 = StatistikManager.fromdict(
            {"statistiken": {"FrageeinheitChinesischBedeutung": {
                    "modus": "PRUEFEN", "antworten": [{"antwort": 6, "erzeugt": 10}]*5},
             "FrageeinheitChinesischPinyin": {
                    "modus": "NEU", "antworten": []}}
             })

    def test_filter_pruefen(self):
        self.assertFalse(StatistikfilterPruefen().filter(self.stat_manager, FrageeinheitChinesischBedeutung,
                                                         24 * 3_600_000))
        self.assertTrue(StatistikfilterPruefen().filter(self.stat_manager, FrageeinheitChinesischBedeutung,
                                                        24 * 3_600_000 + 1))
        self.assertFalse(StatistikfilterPruefen().filter(self.stat_manager, FrageeinheitChinesischPinyin,
                                                         14 * 24 * 3_600_000))
        self.assertFalse(StatistikfilterPruefen().filter(self.stat_manager, FrageeinheitChinesischEintrag,
                                                         14 * 24 * 3_600_000))

    def test_filter_neu(self):
        self.assertFalse(StatistikfilterNeue().filter(self.stat_manager, FrageeinheitChinesischBedeutung,
                                                      24 * 3_600_000))
        self.assertFalse(StatistikfilterNeue().filter(self.stat_manager, FrageeinheitChinesischPinyin,
                                                      2 * 24 * 3_600_000))
        self.assertFalse(StatistikfilterNeue().filter(self.stat_manager2, FrageeinheitChinesischPinyin,
                                                     2 * 24 * 3_600_000), "Vorherige Abfrage noch unter 14 Tagen")
        self.assertTrue(StatistikfilterNeue().filter(self.stat_manager3, FrageeinheitChinesischPinyin,
                                                     2 * 24 * 3_600_000), "Vorherige Abfrage ueber 14 T")
        self.assertFalse(StatistikfilterNeue().filter(self.stat_manager3, FrageeinheitChinesischPinyin,
                                                      10 + 0), "Vorherige Abfrage ueber 14 T, aber Zeit zu frueh")
        self.assertTrue(StatistikfilterNeue().filter(self.stat_manager3, FrageeinheitChinesischPinyin,
                                                     11 + 0), "Vorherige Abfrage ueber 14 T und Zeit ok")
        self.assertFalse(StatistikfilterNeue().filter(self.stat_manager, FrageeinheitChinesischEintrag,
                                                      24 * 3_600_000), "Vorherige Abfrage LernenModus")

    def test_filter_lernen(self):
        self.assertFalse(StatistikfilterLernen().filter(self.stat_manager, FrageeinheitChinesischBedeutung,
                                                        24 * 3_600_000))
        self.assertFalse(StatistikfilterLernen().filter(self.stat_manager, FrageeinheitChinesischPinyin,
                                                        0))
        self.assertTrue(StatistikfilterLernen().filter(self.stat_manager, FrageeinheitChinesischPinyin,
                                                       1 * 24 * 3_600_000 + 1))
        self.assertFalse(StatistikfilterLernen().filter(self.stat_manager, FrageeinheitChinesischEintrag,
                                                        24 * 3_600_000))

    def test_filter_alle_lernen(self):
        self.assertFalse(StatistikfilterLernenAlle().filter(self.stat_manager, FrageeinheitChinesischBedeutung,
                                                            24 * 3_600_000))
        self.assertTrue(StatistikfilterLernenAlle().filter(self.stat_manager, FrageeinheitChinesischPinyin,
                                                           0))
        self.assertTrue(StatistikfilterLernenAlle().filter(self.stat_manager, FrageeinheitChinesischPinyin,
                                                           1 * 24 * 3_600_000 + 1))
        self.assertFalse(StatistikfilterLernenAlle().filter(self.stat_manager, FrageeinheitChinesischEintrag,
                                                            24 * 3_600_000))
