from unittest import TestCase
from unittest.mock import patch, call, ANY
from dataclasses import replace
from typing import Callable, cast

from src.zustaende.zustand import Zustand, ZustandENDE, ZustandBoxinfo
from src.zustaende.zustandstart import ZustandStart
from src.zustaende.zustandveraenderlernuhr import ZustandVeraenderLernuhr
from src.zustaende.zustandvokabeltesten import ZustandVokabelTesten


class test_ZustandStart(TestCase):

    def test_init_zustand_start(self):
        objekt = ZustandStart()
        self.assertIsInstance(objekt, ZustandStart)
        self.assertIsInstance(objekt, Zustand)
        self.assertEqual('Zustand 1', objekt.titel)
        self.assertEqual('Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.',
                         objekt.beschreibung)
        self.assertEqual(('+', '-', '=', 's'), objekt.kommandos)
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])

    def test_parse_user_eingabe_zustand_start(self):
        objekt = ZustandStart(aktueller_index=0, liste=["A", "B"])
        fun, args = objekt.parse_user_eingabe(list(''))
        self.assertEqual(fun, '')
        self.assertEqual(tuple(), args)
        fun, args = objekt.parse_user_eingabe(list('+1'))
        self.assertEqual("CmdStartChangeAktuellenIndex", fun)
        self.assertEqual((1,), args)
        fun, args = objekt.parse_user_eingabe(list('+5'))
        self.assertEqual("CmdStartChangeAktuellenIndex", fun)
        self.assertEqual((1,), args)
        fun, args = objekt.parse_user_eingabe(list('-5'))
        self.assertEqual("CmdStartChangeAktuellenIndex", fun)
        self.assertEqual((0,), args)
        fun, args = objekt.parse_user_eingabe(list('=1'))
        self.assertEqual("CmdStartChangeAktuellenIndex", fun)
        self.assertEqual((1,), args)
        fun, args = objekt.parse_user_eingabe(list('s'))
        self.assertEqual("CmdSpeicherRepositories", fun)
        self.assertEqual(tuple(), args)
