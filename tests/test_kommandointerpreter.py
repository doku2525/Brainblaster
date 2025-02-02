from unittest import TestCase
from typing import cast
from dataclasses import dataclass, field

from src.classes.vokabeltrainercontroller import VokabeltrainerController
from src.kommandos.kommandointerpreter import KommandoInterpreter
from src.kommandos.kommando import Kommando


class CmdMockerFoo(Kommando):
    """KommandoKlasse fuer die Methode foo() in MockFoo"""
    def execute(self, controller: VokabeltrainerController) -> VokabeltrainerController:
        return controller.foo()


@dataclass
class MockFoo:
    wert: int = field(default=0)

    def foo(self) -> VokabeltrainerController:
        return cast(VokabeltrainerController, MockFoo(self.wert + 10))


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
        result = self.interpreter.execute("CmdMockerFoo", cast(VokabeltrainerController, objekt))
        self.assertEqual(10, result.wert)

    def test_execute_unvalid(self):
        objekt = MockFoo(wert=0)
        self.assertEqual(0, objekt.wert)
        result = self.interpreter.execute("CmdMocker", cast(VokabeltrainerController, objekt))
        # Unbekannte Kommandos liefern das Objekt unveraendert zurueck.
        self.assertEqual(0, result.wert)
