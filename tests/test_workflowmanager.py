from unittest import TestCase
from typing import Type, List
from dataclasses import dataclass, replace

# Importiere deine WorkflowManager- und Zustandsklassen hier
# (angenommen, sie sind in `workflow.py` definiert)
from src.zustaende.workflowmanager import WorkflowManager
from src.zustaende.zustand import Zustand


# Mock-Zustände für Tests
@dataclass(frozen=True)
class MockStateA(Zustand):
    titel: str = "StateA"


@dataclass(frozen=True)
class MockStateB(Zustand):
    titel: str = "StateB"


@dataclass(frozen=True)
class MockStateC(Zustand):
    titel: str = "StateC"


class TestWorkflowManager(TestCase):
    def setUp(self):
        # Initialisiere WorkflowManager mit Test-Transitionen
        self.workflow = WorkflowManager()
        self.transitions = {
            MockStateA: [MockStateB, MockStateC],
            MockStateB: [MockStateA],
            MockStateC: []  # Keine erlaubten Übergänge
        }
        self.workflow = self.workflow.register_transitions(self.transitions)
        self.workflow = replace(self.workflow, aktueller_zustand=MockStateA)

    def test_initial_state(self):
        # Teste Initialisierung
        self.assertEqual(self.workflow.aktueller_zustand, MockStateA)
        self.assertEqual(len(self.workflow.zustands_history), 0)

    def test_valid_transition(self):
        # Teste erlaubten Übergang: A → B
        neuer_zustand = self.workflow.transition_zu(MockStateB)
        self.assertEqual(neuer_zustand.aktueller_zustand, MockStateB)
        self.assertNotEqual(self.workflow.aktueller_zustand, neuer_zustand.aktueller_zustand)
        self.assertEqual(len(self.workflow.zustands_history), 0)
        self.assertEqual(len(neuer_zustand.zustands_history), 1)

    def test_invalid_transition(self):
        # Teste unerlaubten Übergang: A → C (nicht in Transitionen)
        neuer_zustand = self.workflow.transition_zu(MockStateB)
        with self.assertRaises(ValueError):
            neuer_zustand.transition_zu(MockStateC)

    def test_transition_zu_mit_namen_valid(self):
        neuer_zustand = self.workflow.transition_zu_per_namen("MockStateB")
        self.assertEqual(neuer_zustand.aktueller_zustand, MockStateB)
        self.assertNotEqual(self.workflow.aktueller_zustand, neuer_zustand.aktueller_zustand)
        self.assertEqual(len(self.workflow.zustands_history), 0)
        self.assertEqual(len(neuer_zustand.zustands_history), 1)

    def test_transition_zu_mit_gleichen_namen_wie_aktuell(self):
        self.assertEqual(self.workflow,self.workflow.transition_zu_per_namen("MockStateA"))

    def test_transition_zu_mit_namen_invalid(self):
        with self.assertRaises(ValueError):
            self.workflow.transition_zu_per_namen("MockStateF")

    def test_transition_zu_mit_index_valid(self):
        neuer_zustand = self.workflow.transition_zu_per_index(0)
        self.assertEqual(neuer_zustand.aktueller_zustand, MockStateB)
        self.assertNotEqual(self.workflow.aktueller_zustand, neuer_zustand.aktueller_zustand)
        self.assertEqual(len(self.workflow.zustands_history), 0)
        self.assertEqual(len(neuer_zustand.zustands_history), 1)

    def test_transition_zu_mit_index_invalid(self):
        with self.assertRaises(ValueError):
            self.workflow.transition_zu_per_index(100)

    def test_go_back(self):
        # Teste "Zurück"-Funktion: A → B → zurück zu A
        neuer_zustand = self.workflow.transition_zu(MockStateB)
        prev_state = neuer_zustand.go_back()
        self.assertEqual(prev_state.aktueller_zustand, MockStateA)
        self.assertEqual(len(prev_state.zustands_history), 0)
        self.assertEqual(len(neuer_zustand.zustands_history), 1)

    def test_history_after_multiple_transitions(self):
        # Teste History nach mehreren Übergängen: A → B → A
        neuer_zustand = self.workflow.transition_zu(MockStateB)
        neuer_zustand = neuer_zustand.transition_zu(MockStateA)
        self.assertEqual(len(neuer_zustand.zustands_history), 2)
        self.assertEqual(neuer_zustand.zustands_history[0], MockStateA)
        self.assertEqual(neuer_zustand.zustands_history[1], MockStateB)

    def test_transition_registration(self):
        # Teste, ob Transitionen korrekt registriert wurden
        self.assertEqual(
            self.workflow.transitions[MockStateA],
            [MockStateB, MockStateC]
        )

    def test_go_back_with_empty_history(self):
        # Teste "Zurück" ohne History
        initial_state = self.workflow.aktueller_zustand
        prev_state = self.workflow.go_back()  # Keine History vorhanden
        self.assertIs(prev_state, initial_state)
