from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Type, Optional


@dataclass(frozen=True)
class WorkflowManager:
    transitions: dict[Type[Zustand], list[Type[Zustand]]] = field(default_factory=dict)
    aktueller_zustand: Optional[Type[Zustand]] = None
    zustands_history: list[Zustand] = field(default_factory=list)  # Für "Zurück"-Navigation

    def _get_aktuelle_transistions(self) -> list[Type[Zustand]]:
        return self.transitions.get(self.aktueller_zustand, [])

    def transition_zu(self, neuer_zustands_typ: Type[Zustand], parent: Zustand = None) -> WorkflowManager:
        """
        Ersetze aktuellen Zustand durch neuen Zustand, wenn der neue Zustand in der Liste der moeglichen Transition
        des aktuellen Zustands ist, und liefer dern veraenderten WorkflowManager zurueck
        Wenn der neue Zustand und der aktuelle Zustand identisch sind, dann den aktuelle WorkflowManager unveraendert.
        Ansonsten werfe Fehler
        :param neuer_zustands_typ: Type[Zustand]
        :param parent: # Kann geloescht werden
        :return: WorkflowManager
        """
        if neuer_zustands_typ == self.aktueller_zustand:
            return self

        # Validiere den Übergang
        erlaubt = self._get_aktuelle_transistions()
        if neuer_zustands_typ not in erlaubt:
            raise ValueError(f"Ungültiger Übergang von {self.aktueller_zustand} zu {neuer_zustands_typ}")

        return replace(self,
                       aktueller_zustand=neuer_zustands_typ,
                       zustands_history=self.zustands_history + [self.aktueller_zustand])

    def transition_zu_per_namen(self, neuer_zustand: str) -> WorkflowManager:
        """
        Suche Transistionziel per String. Funktion fuer die Views, die den Namen des Zustands als String liefern.
        """
        if neuer_zustand == self.aktueller_zustand.__name__:
            return self
        neuer_zustands_typ = [zustand
                              for zustand
                              in self._get_aktuelle_transistions() if zustand.__name__ == neuer_zustand]
        if neuer_zustands_typ:
            return self.transition_zu(neuer_zustands_typ[0])
        else:
            raise ValueError(f"Ungültiger Übergang String {neuer_zustand} nicht gefunden")

    def transition_zu_per_index(self, index: int) -> WorkflowManager:
        """
        Ersetzt den aktuellen Zustand durch den Zustand an Position index innerhalb der Transitions.
        Wenn index > Anzahl der Zustaende in Transitions wird ValueError geworfen.
        :param index: int
        :return: WorkflowManager
        """
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
