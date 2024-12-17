from unittest import TestCase
from datetime import date
from time import sleep, time

from src.classes.lernuhr import Lernuhr
from src.classes.lernuhr import UhrStatus


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
        self.unix_zeit_string = '1970-01-01 01:00:00.000000'

    def test_echte_zeit(self):
        sleep(0.2)
        self.assertLess(self.jetzt, Lernuhr.echte_zeit(), "jetzt < als aktuelleZeit")
        self.assertFalse(self.jetzt > Lernuhr.echte_zeit(), "jetzt ist nicht > als aktuelleZeit")
        self.assertAlmostEqual(time() * 1000, Lernuhr.echte_zeit(), delta=2)

    def test_speicher_in_jsondatei(self):
        dateiname = '__uhr.json'
        uhr = Lernuhr()
        uhr.speicher_in_jsondatei(dateiname)
        with open(dateiname, "r") as file:
            string = file.read()
        dic = eval(string)
        self.assertEqual('1970-01-01 01:00:00.000000', dic['kalkulations_zeit'])
        self.assertEqual('1970-01-01 01:00:00.000000', dic['start_zeit'])
        self.assertEqual(1.0, dic['tempo'])
        self.assertEqual(0, dic['pause'])
        self.assertEqual('ECHT', dic['modus'])
        uhr = Lernuhr(1720743153000, 1720743153000, 1.0, 0, UhrStatus.LAEUFT)
        uhr.speicher_in_jsondatei(dateiname)
        with open(dateiname, "r") as file:
            string = file.read()
        dic = eval(string)
        self.assertEqual('2024-07-12 02:12:33.000000', dic['kalkulations_zeit'])
        self.assertEqual('2024-07-12 02:12:33.000000', dic['start_zeit'])
        self.assertEqual(1.0, dic['tempo'])
        self.assertEqual(0, dic['pause'])
        self.assertEqual('LAEUFT', dic['modus'])

    def test_lade_aus_jsondatei(self):
        dateiname = '__uhr.json'
        uhr = Lernuhr.lade_aus_jsondatei(dateiname)
        uhr2 = Lernuhr(1720743153000, 1720743153000, 1.0, 0, UhrStatus.LAEUFT)
        self.assertEqual(uhr, uhr2)
        self.assertIsInstance(uhr.kalkulations_zeit, int)
        self.assertIsInstance(uhr.start_zeit, int)
        self.assertIsInstance(uhr.modus, UhrStatus)
        self.assertIsInstance(uhr.pause, int)
        self.assertIsInstance(uhr.tempo, float)

    def test_isostring_to_millis(self):
        self.assertEquals(Lernuhr.isostring_to_millis('1970-01-01 01:00'), 0)

    def test_now_kalkzeit_eq_startzeit(self):
        uhr = Lernuhr(0, 0, 1, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, 0, 2, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-03 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, 0, 0.5, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 13:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, 0, 1, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, 0, 2, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, 0, 0.5, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(self.einTag))

    def test_now_kalkzeit_lt_startzeit(self):
        uhr = Lernuhr(0, self.einTag, 1, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-03 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, self.einTag, 2, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-04 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, self.einTag, 0.5, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-02 13:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, self.einTag, 1, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, self.einTag, 2, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(0, self.einTag, 0.5, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-02 01:00:00.000000', uhr.as_iso_format(self.einTag))

    def test_now_kalkzeit_gt_startzeit(self):
        uhr = Lernuhr(self.einTag, 0, 1, 0, UhrStatus.LAEUFT)
        self.assertEqual('1969-12-31 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(self.einTag, 0, 2, 0, UhrStatus.LAEUFT)
        self.assertEqual('1969-12-30 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(self.einTag, 0, 0.5, 0, UhrStatus.LAEUFT)
        self.assertEqual('1969-12-31 13:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(self.einTag, 0, 1, 0, UhrStatus.PAUSE)
        self.assertEqual('1969-12-31 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1969-12-31 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(self.einTag, 0, 2, 0, UhrStatus.PAUSE)
        self.assertEqual('1969-12-30 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1969-12-30 01:00:00.000000', uhr.as_iso_format(self.einTag))
        uhr = Lernuhr(self.einTag, 0, 0.5, 0, UhrStatus.PAUSE)
        self.assertEqual('1969-12-31 13:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1969-12-31 13:00:00.000000', uhr.as_iso_format(self.einTag))

    def test_now_vergleich(self):
        uhr_normal = Lernuhr(0, self.einTag, 1, 0, UhrStatus.LAEUFT)
        uhr_schnell = Lernuhr(0, self.einTag, 2, 0, UhrStatus.LAEUFT)
        uhr_langsam = Lernuhr(0, self.einTag, 0.5, 0, UhrStatus.LAEUFT)
        self.assertEqual(uhr_normal.now(self.einTag * 100), uhr_schnell.now(self.einTag * 50))
        self.assertEqual(uhr_normal.now(self.einTag * 100), uhr_langsam.now(self.einTag * 200))

        uhr_normal = Lernuhr(0, self.einTag, 1, 0, UhrStatus.PAUSE)
        uhr_schnell = Lernuhr(0, self.einTag, 2, 0, UhrStatus.PAUSE)
        uhr_langsam = Lernuhr(0, self.einTag, 0.5, 0, UhrStatus.PAUSE)
        self.assertEqual(uhr_normal.now(self.einTag * 100), uhr_schnell.now(self.einTag * 50))
        self.assertEqual(uhr_normal.now(self.einTag * 100), uhr_schnell.now(self.einTag * 100))
        self.assertEqual(uhr_normal.now(self.einTag * 100), uhr_langsam.now(self.einTag * 200))
        self.assertEqual(uhr_normal.now(self.einTag * 100), uhr_langsam.now(self.einTag * 100))

    def test_now_gegenwart(self):
        zeit_jetzt = Lernuhr.isostring_to_millis('2024-12-01 01:00:00.000000')
        uhr = Lernuhr(zeit_jetzt, zeit_jetzt, 1, 0, UhrStatus.LAEUFT)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('2024-12-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt))
        self.assertEqual('2024-12-02 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag))
        uhr = Lernuhr(zeit_jetzt, zeit_jetzt, 1, 0, UhrStatus.PAUSE)
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt))
        self.assertNotEqual('2024-12-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt))
        self.assertEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag))
        self.assertNotEqual('2024-12-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag))
        uhr = Lernuhr(zeit_jetzt, zeit_jetzt, 1, zeit_jetzt, UhrStatus.PAUSE)
        self.assertEqual('2024-12-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertNotEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(0))
        self.assertNotEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt))
        self.assertEqual('2024-12-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt))
        self.assertNotEqual('1970-01-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag))
        self.assertEqual('2024-12-01 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag))

    def test_now_zehn_tage_testfall(self):
        heute = self.einTag * 10
        uhr = Lernuhr(heute, 0, 2, 0, UhrStatus.LAEUFT)
        for tag in range(0, 10):
            self.assertEqual(f"1970-01-{1 + tag*2:02d} 01:00:00.000000",
                             uhr.as_iso_format(heute + self.einTag * tag))

    def test_pausiere_neu(self):
        zeit_jetzt = Lernuhr.isostring_to_millis('2024-12-01 01:00:00.000000')
        uhr = Lernuhr(zeit_jetzt, zeit_jetzt, 1, 0, UhrStatus.LAEUFT)
        obj = uhr.pausiere()
        self.assertEqual(0, obj.pause)
        self.assertEqual('1970-01-01 01:00:00.000000', obj.as_iso_format(zeit_jetzt))
        # Ein pausierendes Objekt liefert mit now() immer die Zeit in obj.pause zurueck.
        obj = uhr.pausiere(zeit_jetzt + self.einTag)
        self.assertEqual(zeit_jetzt + self.einTag, obj.pause)
        self.assertEqual('2024-12-02 01:00:00.000000', obj.as_iso_format(0))
        self.assertEqual('2024-12-02 01:00:00.000000', obj.as_iso_format(zeit_jetzt))
        self.assertEqual('2024-12-02 01:00:00.000000', obj.as_iso_format(zeit_jetzt * 2))
        # pausiere() auf ein Objekt Uhr das bereits pausiert veraendert nichts
        obj = obj.pausiere(zeit_jetzt + self.einTag)
        self.assertEqual('2024-12-02 01:00:00.000000', obj.as_iso_format(zeit_jetzt + 2 * self.einTag))

    def test_beende_pause(self):
        zeit_jetzt = Lernuhr.isostring_to_millis('2024-12-01 01:00:00.000000')
        uhr_ohne_pause = Lernuhr(zeit_jetzt, zeit_jetzt, 1, 0, UhrStatus.LAEUFT)
        tage_vergangen = 1
        uhr = uhr_ohne_pause.pausiere(zeit_jetzt + self.einTag * tage_vergangen)
        self.assertEqual(zeit_jetzt + self.einTag * tage_vergangen,
                         uhr.pause, "pause wird auf den Beginn der Pause gesetzt")
        tage_vergangen = 2
        uhr = uhr.beende_pause(zeit_jetzt + self.einTag * tage_vergangen)
        self.assertEqual(0, uhr.pause, "pause wird wieder auf 0 gesetzt")
        self.assertEqual('1969-12-31 01:00:00.000000', uhr.as_iso_format(0))
        self.assertEqual('2024-12-02 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag * tage_vergangen))
        self.assertEqual('2024-12-03 01:00:00.000000',
                         uhr_ohne_pause.as_iso_format(zeit_jetzt + self.einTag * tage_vergangen))
        tage_vergangen = 3
        self.assertEqual('2024-12-03 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + self.einTag * tage_vergangen))
        self.assertEqual('2024-12-04 01:00:00.000000',
                         uhr_ohne_pause.as_iso_format(zeit_jetzt + self.einTag * tage_vergangen))

    def test_reset_neu(self):
        zeit_jetzt = Lernuhr.isostring_to_millis('2024-12-01 01:00:00.000000')
        uhr = Lernuhr(zeit_jetzt, zeit_jetzt, 2, 0, UhrStatus.LAEUFT)
        self.assertEqual('2024-12-05 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + 2 * self.einTag))
        uhr_reseted = uhr.reset(zeit_jetzt + 2 * self.einTag)
        self.assertEqual('2024-12-09 01:00:00.000000', uhr.as_iso_format(zeit_jetzt + 4 * self.einTag))
        self.assertEqual('2024-12-05 01:00:00.000000', uhr_reseted.as_iso_format(zeit_jetzt + 4 * self.einTag))

    def test_reset(self):
        sleep(1)
        self.assertGreater(self.normal.now(Lernuhr.echte_zeit()),
                           self.normal.reset(Lernuhr.echte_zeit()).now(Lernuhr.echte_zeit()),
                           "Nach Reset ist die Zeit zurueckgesetzt")

    def test_recalibrate(self):
        objekt = Lernuhr(100_000, 0, 1.0, 0, UhrStatus.LAEUFT)
        self.assertEqual(100_000, objekt.now(200_000))
        self.assertEqual(100_000, objekt.recalibrate(200_000).start_zeit)
        self.assertNotEqual(100_000, objekt.recalibrate(200_000).now(200_000))
        self.assertEqual(100_000, objekt.recalibrate(200_000).reset(200_000).now(200_000))

    def test_as_iso_format(self):
        uhr = Lernuhr(0, 0, 0, 0, UhrStatus.PAUSE)
        self.assertEquals(uhr.as_iso_format()[:-7], '1970-01-01 01:00:00')
        uhr = Lernuhr(1720743153000, 1720743153000, 0, 0, UhrStatus.PAUSE)
        print(f"\n {uhr.as_iso_format()=}")
        self.assertEquals(uhr.as_iso_format()[:-7], '2024-07-12 02:12:33')

    def test_as_date(self):
        uhr = Lernuhr(0, 0, 0, 0, UhrStatus.PAUSE)
        self.assertEqual(date(1970, 1, 1), uhr.as_date())

    def test_iso_dict(self):
        uhr = Lernuhr()
        dic = uhr.as_iso_dict()
        print(f"\n<{dic}>")
        self.assertEqual('1970-01-01 01:00:00.000000', dic['kalkulations_zeit'])
        self.assertEqual('1970-01-01 01:00:00.000000', dic['start_zeit'])
        self.assertEqual(1.0, dic['tempo'])
        self.assertEqual(0, dic['pause'])
        self.assertEqual('ECHT', dic['modus'])
        uhr = Lernuhr(1720743153000, 1720743153000, 1.0, 0, UhrStatus.LAEUFT)
        dic = uhr.as_iso_dict()
        print(f"\n<{dic}>")
        self.assertEqual('2024-07-12 02:12:33.000000', dic['kalkulations_zeit'])
        self.assertEqual('2024-07-12 02:12:33.000000', dic['start_zeit'])
        self.assertEqual(1.0, dic['tempo'])
        self.assertEqual(0, dic['pause'])
        self.assertEqual('LAEUFT', dic['modus'])

    def test_from_iso_dict(self):
        dict_uhr1 = {'kalkulations_zeit': '1970-01-01 01:00:00.000000',
                     'start_zeit': '1970-01-01 01:00:00.000000',
                     'tempo': 1.0,
                     'pause': 0,
                     'modus': 'ECHT'}
        dict_uhr2 = {'kalkulations_zeit': '2024-07-12 02:12:33.000000',
                     'start_zeit': '2024-07-12 02:12:33.000000',
                     'tempo': 2.0,
                     'pause': 0,
                     'modus': 'LAEUFT'}
        uhr = Lernuhr.from_iso_dict(dict_uhr1)
        self.assertEqual(0, uhr.kalkulations_zeit)
        self.assertEqual(0, uhr.start_zeit)
        self.assertEqual(1, uhr.tempo)
        self.assertEqual(0, uhr.pause)
        self.assertEqual(UhrStatus.ECHT, uhr.modus)
        self.assertEqual(uhr, Lernuhr())
        uhr = Lernuhr.from_iso_dict(dict_uhr2)
        self.assertEqual(1720743153000, uhr.kalkulations_zeit)
        self.assertEqual(1720743153000, uhr.start_zeit)
        self.assertEqual(2, uhr.tempo)
        self.assertEqual(0, uhr.pause)
        self.assertEqual(UhrStatus.LAEUFT, uhr.modus)
        self.assertEqual(uhr, Lernuhr(1720743153000, 1720743153000, 2.0, 0, UhrStatus.LAEUFT))
