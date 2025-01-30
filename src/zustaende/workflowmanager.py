from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Type, Optional


@dataclass(frozen=True)
class WorkflowManager:
    transitions: dict[Type[Zustand], list[Type[Zustand]]] = field(default_factory=dict)
    aktueller_zustand: Optional[Zustand] = None
    zustands_history: list[Zustand] = field(default_factory=list)  # Für "Zurück"-Navigation

    def _get_aktuelle_transistions(self) -> list[Type[Zustand]]:
        return self.transitions.get(type(self.aktueller_zustand), [])

    def transition_zu(self, neuer_zustands_typ: Type[Zustand], parent: Zustand = None) -> WorkflowManager:
        # Validiere den Übergang
        erlaubt = self._get_aktuelle_transistions()
        if neuer_zustands_typ not in erlaubt:
            raise ValueError(f"Ungültiger Übergang von {type(self.aktueller_zustand)} zu {neuer_zustands_typ}")

        # Erzeuge den neuen Zustand mit Parent-Referenz
        neuer_zustand = neuer_zustands_typ(parent=self.aktueller_zustand)
        return replace(self,
                       aktueller_zustand=neuer_zustand,
                       zustands_history=self.zustands_history + [self.aktueller_zustand])

    def transition_zu_per_namen(self, neuer_zustand: str) -> WorkflowManager:
        """Suche Transistionziel per String"""
        neuer_zustands_typ = [zustand
                              for zustand
                              in self._get_aktuelle_transistions() if zustand.__name__ == neuer_zustand]
        if neuer_zustands_typ:
            return self.transition_zu(neuer_zustands_typ[0])
        else:
            raise ValueError(f"Ungültiger Übergang String {neuer_zustand} nicht gefunden")

    def transition_zu_per_index(self, index: int) -> WorkflowManager:
        neuer_zustands_typ = [zustand
                              for counter, zustand
                              in enumerate(self._get_aktuelle_transistions()) if counter == index]
        if neuer_zustands_typ:
            return self.transition_zu(neuer_zustands_typ[0])
        else:
            raise ValueError(f"Ungültiger Übergang Index {index} nicht vorhanden.")

    def go_back(self) -> WorkflowManager:
        if not self.zustands_history:
            return self.aktueller_zustand
        return replace(self,
                       aktueller_zustand=self.zustands_history[-1],
                       zustands_history=self.zustands_history[:-1])

    def register_transitions(self, transitions: dict[Type[Zustand], list[Type[Zustand]]]) -> WorkflowManager:
        return replace(self, transitions=self.transitions | transitions)  # Verbinde beide dicts mit "|"
