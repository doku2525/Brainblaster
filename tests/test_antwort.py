from unittest import TestCase
from antwort import Antwort


class test_Antwort(TestCase):

    def setUp(self):
        self.ant1 = Antwort(5, 2000)
        self.ant2 = Antwort(3, 3000)
        self.ant3 = Antwort(7, 3000)
        self.ant4 = Antwort(0, 3000)

    def test_ist_richtig(self):
        self.assertTrue(self.ant1.ist_richtig(), "5 ist richtig")
        self.assertFalse(self.ant2.ist_richtig(), "3 ist nicht richtig")
        self.assertFalse(self.ant3.ist_richtig(), "7 ist nicht richtig")
        self.assertFalse(self.ant4.ist_richtig(), "0 ist richtig")

    def test_ist_falsch(self):
        self.assertFalse(self.ant1.ist_falsch(), "5 ist nicht falsch")
        self.assertTrue(self.ant2.ist_falsch(), "3 ist falsch")
        self.assertFalse(self.ant3.ist_falsch(), "7 ist nicht falsch")
        self.assertFalse(self.ant4.ist_falsch(), "0 ist nicht falsch")

    def test_ist_richtig_gelernt(self):
        self.assertFalse(self.ant1.ist_richtig_gelernt(), "5 ist nicht richtiggelernt")
        self.assertFalse(self.ant2.ist_richtig_gelernt(), "3 ist nicht richtiggelernt")
        self.assertTrue(self.ant3.ist_richtig_gelernt(), "7 ist richtiggelernt")
        self.assertFalse(self.ant4.ist_richtig_gelernt(), "0 ist nicht richtiggelernt")

    def test_ist_falsch_gelernt(self):
        self.assertFalse(self.ant1.ist_falsch_gelernt(), "5 ist nicht falschgelernt")
        self.assertFalse(self.ant2.ist_falsch_gelernt(), "3 ist nicht falschgelernt")
        self.assertFalse(self.ant3.ist_falsch_gelernt(), "7 ist nicht falschgelernt")
        self.assertTrue(self.ant4.ist_falsch_gelernt(), "0 ist falschgelernt")

    def test_ist_lernen(self):
        self.assertFalse(self.ant1.ist_lernen(), "5 ist nicht lernen")
        self.assertFalse(self.ant2.ist_lernen(), "3 ist nicht lernen")
        self.assertTrue(self.ant3.ist_lernen(), "7 ist lernen")
        self.assertTrue(self.ant4.ist_lernen(), "0 ist lernen")
