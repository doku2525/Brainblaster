from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Any, Callable


@dataclass(frozen=True)
class Zustand:
    data: dict = field(default_factory=dict)
    parent: Zustand | None = field(default=None)
    child: list[Zustand] = field(default_factory=list)
    beschreibung: str = field(default_factory=str)
    titel: str = field(default_factory=str)
    kommandos: list[str] = field(default_factory=list)

    def daten_text_konsole(self, presenter: Callable[[dict], str] = None) -> str | None:
        """Erzeuge prettyprint-String der Daten des Zsuatnds fuer die Konsole"""
        return presenter(self.data) if presenter else None

    def info_text_konsole(self) -> str:
        """Erzeuge prettyprint-String mit den moeglichen Aktionen des Zustands fuer die Konsole"""
        return (
            f"{'-'*10}\n" +
            "* Die verfuegbaren Zustaende\n" +
            "".join(
                [f"\t{index} {zustand.titel} : {zustand.beschreibung}\n" for index, zustand in enumerate(self.child)]) +
            f"* Die verfuegbaren Kommandos\n" +
            "".join([f"\t'{command}' + Zahl\n" for command in self.kommandos]))

    def verarbeite_userinput(self, index_child: str) -> tuple[Zustand, Callable, tuple]:
        """Verarbeite den userinput"""
        return (self.child[int(index_child)], lambda: None, tuple()) if index_child else (self, lambda: None, tuple())


@dataclass(frozen=True)
class ZustandENDE(Zustand):
    titel: str = field(default='ENDE')
    beschreibung: str = field(default='Beende Programm')

    def info_text_konsole(self) -> str:
        """Erzeuge prettyprint-String mit den moeglichen Aktionen des Zustands fuer die Konsole"""
        return f"Ciao!"


@dataclass(frozen=True)
class ZustandStart(Zustand):
    liste: list[str] = field(default_factory=list)
    aktueller_index: int = 0
    titel: str = 'Zustand 1'
    beschreibung: str = 'Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.'
    child: list[Zustand] = field(default=(ZustandENDE(),))
    kommandos: list[str] = field(default=("+", "-", "="))

    def __post_init__(self):
        object.__setattr__(self,
                           'data',
                           {'liste': self.liste, 'aktueller_index': self.aktueller_index} if self.liste else {})

    def daten_text_konsole(self, presenter: Callable = None) -> str:
        """Erzeuge prettyprint-String der Daten des Zustands fuer die Konsole"""
        return (f" {self.titel}\n" +
                f"\t {self.beschreibung}\n" +
                ''.join([f"{index:2d} : {boxtitel}\n" for index, boxtitel in enumerate(self.liste)]) +
                f" Aktuelle Box: {self.liste[self.aktueller_index]}") if not presenter else presenter(self.data)

    def verarbeite_userinput(self, index_child: str) -> tuple[Zustand, Callable, tuple]:
        """Verarbeite den userinput"""
        if index_child == '':
            return self, lambda: None, tuple()
        if "+" == index_child[0]:
            return (replace(self,
                            aktueller_index=min(len(self.liste)-1, self.aktueller_index + int(index_child[1:]))),
                    lambda: None,
                    tuple())
        if "-" == index_child[0]:
            return (replace(self,
                            aktueller_index=max(0, self.aktueller_index - int(index_child[1:]))),
                    lambda: None,
                    tuple())
        if "=" == index_child[0]:
            kontrollierter_wert = min(len(self.liste)-1, max(0, int(index_child[1:])))
            return replace(self, aktueller_index=kontrollierter_wert), lambda: None, tuple()
        return super().verarbeite_userinput(index_child)
