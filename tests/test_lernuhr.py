from time import sleep
from unittest import TestCase
from dataclasses import asdict

from libs.utils_dataclass import mein_asdict
from lernuhr import Lernuhr, UhrStatus


class test_LernUhr(TestCase):

    def setUp(self):
        self.einTag = (1000 * 60 * 60 * 24 * 1)
        self.dummy = Lernuhr(0, 0, 0, 0, UhrStatus.PAUSE)
        self.jetzt = Lernuhr.echte_zeit()
        self.normal = Lernuhr(self.jetzt, self.jetzt - self.einTag, 1.0, 0, UhrStatus.LAEUFT)
        self.langsam = Lernuhr(self.jetzt, self.jetzt - self.einTag, 0.5, 0, UhrStatus.LAEUFT)
        self.schnell = Lernuhr(self.jetzt, self.jetzt - self.einTag, 2.0, 0, UhrStatus.LAEUFT)
        self.zeit = 2
        self.rest = 1

    def test_fromdict_asdict(self):
        neu = {'kalkulations_zeit': 0, 'start_zeit': 0, 'tempo': 1.0, 'pause': 0, 'modus': 'ECHT'}
        self.assertEqual(neu, mein_asdict(Lernuhr()))
        self.assertEqual(Lernuhr(), Lernuhr.fromdict(mein_asdict(Lernuhr())))
        self.assertEqual(self.normal, Lernuhr.fromdict(mein_asdict(self.normal)))
        self.assertEqual(self.normal, Lernuhr.fromdict(mein_asdict(self.normal)))

    def test_echte_zeit(self):
        sleep(0.2)
        self.assertLess(self.jetzt, Lernuhr.echte_zeit(), "jetzt < als aktuelleZeit")
        self.assertFalse(self.jetzt > Lernuhr.echte_zeit(), "jetzt ist nicht > als aktuelleZeit")

    def test_isostring_to_millis(self):
        self.assertEquals(Lernuhr.isostring_to_millis('1970-01-01 01:00'), 0)

    def test_now(self):
        # TODO Tests neu schreiben, damit die sleep()-Befehle entfallen
        # sleep(1)
        self.assertGreater(self.schnell.now(self.jetzt + 1000),
                           self.normal.now(self.jetzt + 1000), "schnell ist > als normal")
        self.assertLess(self.langsam.now(self.jetzt + 1000),
                        self.normal.now(self.jetzt + 1000), "normal ist > als langsam")
        before = self.schnell.now(Lernuhr.echte_zeit())
        sleep(self.zeit)
        after = self.schnell.now(Lernuhr.echte_zeit())
        self.assertIn(int((after-before)/1000),
                      range(int(self.schnell.tempo * self.zeit) - self.rest,
                            int(self.schnell.tempo * self.zeit) + self.rest),
                      "schnell ist doppelte Geschwindigkeit")
        before = self.normal.now(Lernuhr.echte_zeit())
        sleep(self.zeit)
        after = self.normal.now(Lernuhr.echte_zeit())
        self.assertIn(int((after-before)/1000),
                      range(int(self.normal.tempo*self.zeit)-self.rest,
                            int(self.normal.tempo*self.zeit)+self.rest), "normal ist einfache Geschwindigkeit")
        before = self.langsam.now(Lernuhr.echte_zeit())
        sleep(self.zeit)
        after = self.langsam.now(Lernuhr.echte_zeit())
        self.assertIn(int((after-before)/1000),
                      range(int(self.langsam.tempo*self.zeit)-self.rest, int(self.langsam.tempo*self.zeit)+self.rest),
                      "langsam ist halbe Geschwindigkeit")

    def test_pausiere(self):
        obj = self.normal.pausiere()
        before = obj.now(Lernuhr.echte_zeit())
        sleep(self.zeit)
        after = obj.now(Lernuhr.echte_zeit())
        self.assertIn(int((after-before)/1000),
                      range(int(0-self.rest), self.rest), "bei Pause laeuft die Zeit nicht weiter")
        self.assertEquals(UhrStatus.PAUSE, obj.modus, "Status == PAUSE")
        self.assertIn(int((self.normal.now(Lernuhr.echte_zeit()) - obj.now(Lernuhr.echte_zeit()))/1000),
                      range(self.zeit-self.rest, self.zeit+self.rest), "pause ist $zeit langsamer als normal")

    def test_beende_pause(self):
        obj_a = self.normal.pausiere()
        sleep(self.zeit)
        obj_b = obj_a.beende_pause()
        before = obj_b.now(Lernuhr.echte_zeit())
        sleep(self.zeit)
        after = obj_b.now(Lernuhr.echte_zeit())
        self.assertIn(int((after-before)/1000),
                      range(self.zeit-self.rest, self.zeit+self.rest),
                      "wenn pause beendet, lauft uhr normal weiter")
        self.assertIn(int((self.normal.now(Lernuhr.echte_zeit()) - obj_b.now(Lernuhr.echte_zeit()))/1000),
                      range(self.zeit-self.rest, self.zeit+self.rest),
                      "Nach $zeit ist Uhr immer noch $zeit zurueck")

    def test_reset(self):
        sleep(1)
        self.assertGreater(self.normal.now(Lernuhr.echte_zeit()), self.normal.reset().now(Lernuhr.echte_zeit()),
                           "Nach Reset ist die Zeit zurueckgesetzt")

    def test_as_iso_format(self):
        uhr = Lernuhr(0, 0, 0, 0, UhrStatus.PAUSE)
        self.assertEquals(uhr.as_iso_format()[:-7], '1970-01-01 01:00:00')

    def test_as_date(self):
        # TODO Methode noch nicht implementiert
        assert False
