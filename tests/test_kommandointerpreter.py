from unittest import TestCase
from typing import cast
from dataclasses import dataclass, field
from typing import Callable, Any

from src.classes.vokabeltrainercontroller import VokabeltrainerController
from src.kommandos.kommandointerpreter import KommandoInterpreter
from src.kommandos.kommando import Kommando


class CmdMockerFoo(Kommando):
    """KommandoKlasse fuer die Methode foo() in MockFoo"""
    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        def funktion(zahl):
            return controller.foo(zahl)
        return funktion


@dataclass
class MockFoo:
    wert: int = field(default=0)

    def foo(self, x: int = 0) -> VokabeltrainerController:
        return cast(VokabeltrainerController, MockFoo(self.wert + 10 + x))


class test_Kommandointerpreter(TestCase):

    def setUp(self):
        self.interpreter = KommandoInterpreter()

    def test_initialization(self):
        # Mindestens unsere MockKommando-Klasse sollte registriert worden sein
        self.assertGreater(len(self.interpreter.cmds), 0)
        self.assertIn("CmdMockerFoo", self.interpreter.cmds.keys())

    def test_build_cmds_mapping(self):
        # Mindestens unsere MockKommando-Klasse sollte registriert worden sein
        result = KommandoInterpreter.build_cmds_mapping(Kommando)
        self.assertGreater(len(result), 0)
        self.assertIn("CmdMockerFoo", result)

    def test_execute_valid(self):
        objekt = MockFoo(wert=0)
        self.assertEqual(0, objekt.wert)
        result = self.interpreter.execute("CmdMockerFoo", cast(VokabeltrainerController, objekt), (1,))
        self.assertEqual(11, result.wert)
        result = self.interpreter.execute("CmdMockerFoo", cast(VokabeltrainerController, objekt), (5,))
        self.assertEqual(15, result.wert)
        with self.assertRaises(TypeError):
            result = self.interpreter.execute("CmdMockerFoo", cast(VokabeltrainerController, objekt))
        with self.assertRaises(TypeError):
            result = self.interpreter.execute("CmdMockerFoo", cast(VokabeltrainerController, objekt), tuple())

    def test_execute_unvalid(self):
        objekt = MockFoo(wert=0)
        self.assertEqual(0, objekt.wert)
        result = self.interpreter.execute("CmdMocker", cast(VokabeltrainerController, objekt), (5,))
        # Unbekannte Kommandos liefern das Objekt unveraendert zurueck.
        self.assertEqual(0, result.wert)
