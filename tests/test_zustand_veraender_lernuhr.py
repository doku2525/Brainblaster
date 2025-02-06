from unittest import TestCase
from unittest.mock import patch, call, ANY
from dataclasses import replace
from typing import Callable, cast

from src.zustaende.zustand import Zustand, ZustandENDE, ZustandBoxinfo
from src.zustaende.zustandstart import ZustandStart
from src.zustaende.zustandveraenderlernuhr import ZustandVeraenderLernuhr
from src.zustaende.zustandvokabeltesten import ZustandVokabelTesten
from src.classes.lernuhr import Lernuhr, UhrStatus
import datetime


class test_ZustandVeraenderLernuhr(TestCase):

    def test_init_zustand(self):
        objekt = ZustandVeraenderLernuhr()
        self.assertIsInstance(objekt, ZustandVeraenderLernuhr)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('ZustandStelleUhr', objekt.titel)
        self.assertEqual('Zustand, zum Stellen der Uhr.', objekt.beschreibung)
        self.assertEqual('', objekt.aktuelle_zeit)
        self.assertIsNone(objekt.neue_uhr)
        self.assertEqual(('c', 'k', 'p', 'r', 's', 't', 'u', 'z'), objekt.kommandos)

    def test_parse_user_eingabe_option_leerer_string(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)
        fun, args = objekt.parse_user_eingabe(list(''))
        self.assertEqual("", fun)
        self.assertEqual(tuple(), args)

    def test_parse_user_eingabe_option_c(self):
        uhr = Lernuhr(kalkulations_zeit=200_000)
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)

        fun, args = objekt.parse_user_eingabe(list('c'))
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertAlmostEqual(gestoppte_zeit, args[0].neue_uhr.start_zeit, delta=1_000)
        self.assertNotAlmostEqual(uhr.start_zeit, args[0].neue_uhr.start_zeit, delta=1_000)

    def test_parse_user_eingabe_option_k_iso(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        iso_string = '2024-01-01 00:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k={iso_string}"))
        sekunden = datetime.datetime.fromisoformat(iso_string).timestamp() * 1000

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(sekunden, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            iso_string,
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_k_plus_tag(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k+1t"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(24 * 60 * 60 * 1000, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-02 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_k_minus_tag(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

        # # iso_string = '2024-01-01 00:00:00'
        # # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k-1t"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(24 * 60 * 60 * -1000, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1969-12-31 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_k_plus_stunde(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k+1h"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * 60 * 1000, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 02:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_k_minus_stunde(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k-1h"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * 60 * -1000, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 00:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_k_plus_minute(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k+1m"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * 1000, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 01:01:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_k_minus_minute(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"k-1m"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * -1000, args[0].neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 00:59:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_parse_user_eingabe_option_p(self):
        # Es gibt eine bestimmte Reihenfolge, die eingehalten werden muss. Siehe auch Issue #35
        # LAEUFT -> ECHT, LAEUFT -> PAUSE, ECHT -> LAEUFT und PAUSE -> LAEUFT sollten wie erwartet funktionieren

        # Startzustand ist Lernuhr in LAEUFT
        uhr = Lernuhr(modus=UhrStatus.LAEUFT)
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)
        self.assertEqual(UhrStatus.LAEUFT, uhr.modus)
        fun, args = objekt.parse_user_eingabe(list('pe'))
        # TODO Im Mediator wird nicht mehr Lernuhr.echte_zeit() aufgerufen, sondern aktuelle_zeit zum Berechnen
        #   der neuen_uhrzeit, dadurch koennte sich der Test veraendern.
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.LAEUFT, args[0].neue_uhr.modus)

        fun, args = objekt.parse_user_eingabe(list('pb'))
        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.PAUSE, args[0].neue_uhr.modus)

        # Startzustand ist Lernuhr in PAUSE
        uhr = Lernuhr(modus=UhrStatus.PAUSE)
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)
        self.assertEqual(UhrStatus.PAUSE, uhr.modus)
        fun, args = objekt.parse_user_eingabe(list('pe'))
        self.assertNotEqual(args[0], objekt)
        self.assertEqual(UhrStatus.LAEUFT, args[0].neue_uhr.modus)

        fun, args = objekt.parse_user_eingabe(list('pb'))
        self.assertEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.PAUSE, args[0].neue_uhr.modus)

    def test_parse_user_eingabe_option_r(self):
        uhr = Lernuhr()
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)

        fun, args = objekt.parse_user_eingabe(list('r'))
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertAlmostEqual(gestoppte_zeit, args[0].neue_uhr.kalkulations_zeit, delta=1_000)
        self.assertNotAlmostEquals(uhr.kalkulations_zeit, args[0].neue_uhr.kalkulations_zeit, delta=1_000)

    def test_parse_user_eingabe_option_s_iso(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        iso_string = '2024-01-01 00:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s={iso_string}"))
        sekunden = datetime.datetime.fromisoformat(iso_string).timestamp() * 1000

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(sekunden, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            iso_string,
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_s_plus_tag(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s+1t"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(24 * 60 * 60 * 1000, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-02 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_s_minus_tag(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

        # # iso_string = '2024-01-01 00:00:00'
        # # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s-1t"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(24 * 60 * 60 * -1000, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            '1969-12-31 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_s_plus_stunde(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s+1h"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * 60 * 1000, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 02:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_s_minus_stunde(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s-1h"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * 60 * -1000, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 00:00:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_s_plus_minute(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s+1m"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * 1000, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 01:01:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_s_minus_minute(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        fun, args = objekt.parse_user_eingabe(list(f"s-1m"))

        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(60 * -1000, args[0].neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 00:59:00',
            f"{datetime.datetime.fromtimestamp(int(args[0].neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_parse_user_eingabe_option_t(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        fun, args = objekt.parse_user_eingabe(list('t1.0'))
        self.assertEqual("CmdErsetzeAktuellenZustand", fun)
        self.assertIsInstance(args[0], ZustandVeraenderLernuhr)
        self.assertEqual(1.0, args[0].neue_uhr.tempo)
        self.assertEqual(1.0, objekt.neue_uhr.tempo)

        fun, args = objekt.parse_user_eingabe(list('t2.0'))
        self.assertEqual("CmdErsetzeAktuellenZustand", fun)
        self.assertIsInstance(args[0], ZustandVeraenderLernuhr)
        self.assertEqual(2.0, args[0].neue_uhr.tempo)
        self.assertEqual(1.0, objekt.neue_uhr.tempo)

        fun, args = objekt.parse_user_eingabe(list('t3'))    # Teste Zahl ohne Kommastelle
        self.assertEqual("CmdErsetzeAktuellenZustand", fun)
        self.assertIsInstance(args[0], ZustandVeraenderLernuhr)
        self.assertEqual(3.0, args[0].neue_uhr.tempo)
        self.assertEqual(1.0, objekt.neue_uhr.tempo)

    def test_parse_user_eingabe_option_z(self):
        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        fun, args = objekt.parse_user_eingabe(list('ze'))
        self.assertEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.ECHT, args[0].neue_uhr.modus)
        self.assertEqual(UhrStatus.ECHT, objekt.neue_uhr.modus)

        fun, args = objekt.parse_user_eingabe(list('zp'))
        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.PAUSE, args[0].neue_uhr.modus)
        self.assertEqual(UhrStatus.ECHT, objekt.neue_uhr.modus)

        fun, args = objekt.parse_user_eingabe(list('zl'))
        self.assertNotEqual(args[0], objekt)
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.LAEUFT, args[0].neue_uhr.modus)
        self.assertEqual(UhrStatus.ECHT, objekt.neue_uhr.modus)

        result = args[0]
        fun, args = result.parse_user_eingabe(list('ze'))
        self.assertNotEqual(result, args[0])
        self.assertEqual('CmdErsetzeAktuellenZustand', fun)
        self.assertEqual(UhrStatus.ECHT, args[0].neue_uhr.modus)
        self.assertEqual(UhrStatus.LAEUFT, result.neue_uhr.modus)
