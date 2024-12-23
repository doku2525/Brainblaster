from unittest import TestCase
from unittest.mock import patch, call, ANY
from dataclasses import replace
from typing import Callable, cast

from src.classes.zustand import Zustand, ZustandENDE, ZustandStart, ZustandVeraenderLernuhr, ZustandBoxinfo


class test_Zustand(TestCase):

    def test_init(self):
        objekt = Zustand()
        self.assertIsInstance(objekt, Zustand)
        self.assertEqual('', objekt.titel)
        self.assertEqual('', objekt.beschreibung)
        self.assertIsNone(objekt.parent)
        self.assertEqual([], objekt.child)
        self.assertEqual([], objekt.kommandos)

    def test_init_zustand_start(self):
        objekt = ZustandStart()
        self.assertIsInstance(objekt, ZustandStart)
        self.assertIsInstance(objekt, Zustand)
        self.assertEqual('Zustand 1', objekt.titel)
        self.assertEqual('Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.',
                         objekt.beschreibung)
        self.assertIsNone(objekt.parent)
        self.assertEqual(1, len(objekt.child))
        self.assertEqual((ZustandENDE(),), objekt.child)
        self.assertEqual(("+", "-", "="), objekt.kommandos)
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])

    def test_init_zustand_ende(self):
        objekt = ZustandENDE()
        self.assertIsInstance(objekt, ZustandENDE)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('ENDE', objekt.titel)
        self.assertEqual('Beende Programm', objekt.beschreibung)

    def test_init_zustand_veraender_lernuhr(self):
        objekt = ZustandVeraenderLernuhr()
        self.assertIsInstance(objekt, ZustandVeraenderLernuhr)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('ZustandStelleUhr', objekt.titel)
        self.assertEqual('Zustand, zum Stellen der Uhr.', objekt.beschreibung)
        self.assertEqual('', objekt.aktuelle_zeit)
        self.assertIsNone(objekt.neue_uhr)
        self.assertEqual(('s', 'k', 't', 'z', 'p', 'r', 'c'), objekt.kommandos)
        self.assertEqual(None, objekt.parent)
        self.assertEqual([], objekt.child)

    def test_init_zustand_boxinfo(self):
        objekt = ZustandBoxinfo()
        self.assertIsInstance(objekt, ZustandBoxinfo)
        self.assertIsInstance(objekt, Zustand)
        self.assertNotIsInstance(objekt, ZustandStart)
        self.assertEqual('Zustand 2', objekt.titel)
        self.assertEqual('Zustand 2, Zeigt die Boxinfos der aktuellen Box an.', objekt.beschreibung)
        self.assertEqual({}, objekt.info)
        self.assertEqual('', objekt.box_titel)
        self.assertEqual('', objekt.aktuelle_frageeinheit)

    def test_verarbeite_userinput(self):
        objekt = Zustand()
        result, fun, args = objekt.verarbeite_userinput('')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)

    def test_position_index_zustand_in_child(self):
        objekt = Zustand()      # child = []
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen('Irgendwas'))
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen('ZustandENDE'))
        objekt = Zustand(child=[ZustandStart(), ZustandVeraenderLernuhr(), ZustandENDE()])
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen(''))
        self.assertEqual('', objekt.position_zustand_in_child_mit_namen('Irgendwas'))
        self.assertEqual('1', objekt.position_zustand_in_child_mit_namen('ZustandStart'))
        self.assertEqual('2', objekt.position_zustand_in_child_mit_namen('ZustandVeraenderLernuhr'))
        self.assertEqual('3', objekt.position_zustand_in_child_mit_namen('ZustandENDE'))

    def test_verarbeite_userinput_mit_zustandsnamen(self):
        objekt = Zustand()      # child = []
        self.assertEqual(objekt, objekt.verarbeite_userinput('@Irgendwas')[0])
        objekt = Zustand(child=[ZustandStart(), ZustandVeraenderLernuhr(), ZustandENDE()])
        self.assertIsInstance(objekt.verarbeite_userinput('@ZustandStart')[0], ZustandStart)
        self.assertIsInstance(objekt.verarbeite_userinput('@ZustandVeraenderLernuhr')[0], ZustandVeraenderLernuhr)
        self.assertIsInstance(objekt.verarbeite_userinput('@ZustandENDE')[0], ZustandENDE)

    def test_verarbeite_userinput_zustand_start(self):
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])
        result, fun, args = objekt.verarbeite_userinput('')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        result, fun, args = objekt.verarbeite_userinput('+1')
        self.assertNotEqual(result, objekt)
        self.assertEqual(result.aktueller_index, 1)
        self.assertIsInstance(fun, str)
#        self.assertIsNone(fun())
        self.assertEqual((1,), args)
        result, fun, args = objekt.verarbeite_userinput('+5')
        self.assertEqual(result.aktueller_index, 1)
        result, fun, args = objekt.verarbeite_userinput('-5')
        self.assertEqual(result.aktueller_index, 0)
        result, fun, args = objekt.verarbeite_userinput('=1')
        self.assertEqual(result.aktueller_index, 1)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_leerer_string(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus

        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)
        result, fun, args = objekt.verarbeite_userinput('')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_z(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus

        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        result, fun, args = objekt.verarbeite_userinput('ze')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.ECHT, result.neue_uhr.modus)
        self.assertEqual(UhrStatus.ECHT, objekt.neue_uhr.modus)

        result, fun, args = objekt.verarbeite_userinput('zp')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.PAUSE, result.neue_uhr.modus)
        self.assertEqual(UhrStatus.ECHT, objekt.neue_uhr.modus)

        result, fun, args = objekt.verarbeite_userinput('zl')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.LAEUFT, result.neue_uhr.modus)
        self.assertEqual(UhrStatus.ECHT, objekt.neue_uhr.modus)

        result_neu, fun, args = result.verarbeite_userinput('ze')
        self.assertNotEqual(result, result_neu)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.ECHT, result_neu.neue_uhr.modus)
        self.assertEqual(UhrStatus.LAEUFT, result.neue_uhr.modus)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_t(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus

        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        result, fun, args = objekt.verarbeite_userinput('t1.0')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(1.0, result.neue_uhr.tempo)
        self.assertEqual(1.0, objekt.neue_uhr.tempo)

        result, fun, args = objekt.verarbeite_userinput('t2.0')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(2.0, result.neue_uhr.tempo)
        self.assertEqual(1.0, objekt.neue_uhr.tempo)

        result, fun, args = objekt.verarbeite_userinput('t3')   # Teste Zahl ohne Kommastelle
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(3.0, result.neue_uhr.tempo)
        self.assertEqual(1.0, objekt.neue_uhr.tempo)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_k(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus
        import datetime

        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        iso_string = '2024-01-01 00:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"k={iso_string}")
        sekunden = datetime.datetime.fromisoformat(iso_string).timestamp() * 1000

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(sekunden, result.neue_uhr.kalkulations_zeit)
        self.assertEqual(
            iso_string,
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"k+1t")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(24 * 60 * 60 * 1000, result.neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-02 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"k-1t")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(24 * 60 * 60 * -1000, result.neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1969-12-31 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"k+1h")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(60 * 60 * 1000, result.neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 02:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"k-1h")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(60 * 60 * -1000, result.neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 00:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"k+1m")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(60 * 1000, result.neue_uhr.kalkulations_zeit)
        self.assertEqual(
            '1970-01-01 01:01:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.kalkulations_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.kalkulations_zeit)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_s(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus
        import datetime

        uhr = Lernuhr()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(Lernuhr.echte_zeit()),
                                         neue_uhr=uhr)

        iso_string = '2024-01-01 00:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"s={iso_string}")
        sekunden = datetime.datetime.fromisoformat(iso_string).timestamp() * 1000

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(sekunden, result.neue_uhr.start_zeit)
        self.assertEqual(
            iso_string,
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"s+1t")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(24 * 60 * 60 * 1000, result.neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-02 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"s-1t")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(24 * 60 * 60 * -1000, result.neue_uhr.start_zeit)
        self.assertEqual(
            '1969-12-31 01:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"s+1h")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(60 * 60 * 1000, result.neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 02:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"s-1h")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(60 * 60 * -1000, result.neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 00:00:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

        # iso_string = '2024-01-01 00:00:00'
        # unix_iso = '1970-01-01 01:00:00'
        result, fun, args = objekt.verarbeite_userinput(f"s+1m")

        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(60 * 1000, result.neue_uhr.start_zeit)
        self.assertEqual(
            '1970-01-01 01:01:00',
            f"{datetime.datetime.fromtimestamp(int(result.neue_uhr.start_zeit / 1000)):%Y-%m-%d %H:%M:%S}")
        self.assertEqual(0, objekt.neue_uhr.start_zeit)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_r(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus

        uhr = Lernuhr()
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)

        result, fun, args = objekt.verarbeite_userinput('r')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertAlmostEqual(gestoppte_zeit, result.neue_uhr.kalkulations_zeit, delta=1_000)
        self.assertNotAlmostEquals(uhr.kalkulations_zeit, result.neue_uhr.kalkulations_zeit, delta=1_000)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_c(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus

        uhr = Lernuhr(kalkulations_zeit=200_000)
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)

        result, fun, args = objekt.verarbeite_userinput('c')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertAlmostEqual(gestoppte_zeit, result.neue_uhr.start_zeit, delta=1_000)
        self.assertNotAlmostEqual(uhr.start_zeit, result.neue_uhr.start_zeit, delta=1_000)

    def test_verarbeite_userinput_zustand_veraender_lernuhr_option_p(self):
        from src.classes.lernuhr import Lernuhr, UhrStatus
        # Es gibt eine bestimmte Reihenfolge, die eingehalten werden muss. Siehe auch Issue #35
        # LAEUFT -> ECHT, LAEUFT -> PAUSE, ECHT -> LAEUFT und PAUSE -> LAEUFT sollten erwartet funktionieren
        uhr = Lernuhr(modus=UhrStatus.LAEUFT)
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)
        self.assertEqual(UhrStatus.LAEUFT, uhr.modus)
        result, fun, args = objekt.verarbeite_userinput('pe')
        # TODO Im Mediator wird nicht mehr Lernuhr.echte_zeit() aufgerufen, sondern aktuelle_zeit zum Berechnen
        #   der neuen_uhrzeit, dadurch koennte sich der Test veraendern.
        # self.assertNotEqual(result, objekt)    # Der Test ist mal erfolgreich und mal nicht wegen der Millisekunden
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.LAEUFT, result.neue_uhr.modus)
        result, fun, args = objekt.verarbeite_userinput('pb')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.PAUSE, result.neue_uhr.modus)

        uhr = Lernuhr(modus=UhrStatus.PAUSE)
        gestoppte_zeit = Lernuhr.echte_zeit()
        objekt = ZustandVeraenderLernuhr(aktuelle_zeit=uhr.as_iso_format(gestoppte_zeit),
                                         neue_uhr=uhr)
        self.assertEqual(UhrStatus.PAUSE, uhr.modus)
        result, fun, args = objekt.verarbeite_userinput('pe')
        self.assertNotEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.LAEUFT, result.neue_uhr.modus)
        result, fun, args = objekt.verarbeite_userinput('pb')
        self.assertEqual(result, objekt)
        self.assertIsNone(fun())
        self.assertEqual(tuple(), args)
        self.assertEqual(UhrStatus.PAUSE, result.neue_uhr.modus)

# TODO Schreibe noch Tests, die die richtige Funktionalitaet der Uhr prueft. Hatte grosse Probleme,
#  weil in der '='-Hilfsfunktion nicht die Funktion iso_to_millis() aus Lerhnuhr, sondern die Funktion aus datetime
#  benutzt wurde und deshalb Sekunden-Werte in mein Millisekunden-Lernuhrsystem kamen.
