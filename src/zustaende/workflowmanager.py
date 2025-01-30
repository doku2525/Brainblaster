from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Dict, List, Type, Optional


@dataclass(frozen=True)
class WorkflowManager:
    transitions: Dict[Type[Zustand], List[Type[Zustand]]] = field(default_factory=dict)
    aktueller_zustand: Optional[Zustand] = None
    zustands_history: List[Zustand] = field(default_factory=list)  # Für "Zurück"-Navigation

    def transition_zu(self, neuer_zustands_typ: Type[Zustand], parent: Zustand = None) -> WorkflowManager:
        # Validiere den Übergang
        erlaubt = self.transitions.get(type(self.aktueller_zustand), [])
        print(f"{erlaubt = }")
        if neuer_zustands_typ not in erlaubt:
            raise ValueError(f"Ungültiger Übergang von {type(self.aktueller_zustand)} zu {neuer_zustands_typ}")

        # Erzeuge den neuen Zustand mit Parent-Referenz
        neuer_zustand = neuer_zustands_typ(parent=self.aktueller_zustand)
        return replace(self,
                       aktueller_zustand=neuer_zustand,
                       zustands_history=self.zustands_history + [self.aktueller_zustand])

    def go_back(self) -> WorkflowManager:
        if not self.zustands_history:
            return self.aktueller_zustand
        # prev_state = self.zustands_history[-1]
        return replace(self,
                       aktueller_zustand=self.zustands_history[-1],
                       zustands_history=self.zustands_history[:-1])

    def register_transitions(self, transitions: Dict[Type[Zustand], List[Type[Zustand]]]) -> WorkflowManager:
        return replace(self, transitions=self.transitions | transitions)
        # self.transitions.update(transitions)