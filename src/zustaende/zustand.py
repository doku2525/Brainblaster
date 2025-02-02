from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Callable, NamedTuple, TYPE_CHECKING, cast


class ZustandReturnValue(NamedTuple):
    zustand: Zustand
    cmd: Callable
    args: tuple


@dataclass(frozen=True)
class Zustand(ABC):
    parent: Zustand | None = field(default=None)
    child: list[Zustand] = field(default_factory=list)
    beschreibung: str = field(default_factory=str)
    titel: str = field(default_factory=str)
    kommandos: list[str] = field(default_factory=list)
    aktuelle_zeit: str = field(default_factory=str)

    def parse_user_eingabe(self, cmd_str: list[str]) -> tuple[str, tuple]:
        """Liest cmd-String und liefert Tuple mit KommandoString und args"""
        return "", tuple()   # Abstarkte Klasse, deshalb gibt es keine Kommandos

    def position_zustand_in_child_mit_namen(self, klassen_name: str) -> str:
        """Da 0 fuer die Position parrent reserviert ist, ist result = '' oder '1..n'  """
        return "".join([str(index)
                        for index, zustand
                        in enumerate(self.child, 1) if zustand.__class__.__name__ == klassen_name])

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        """Verarbeite den userinput.
        Der normale userinput, der nicht gefiltert wird ist eine Zahl, die die Position innerhalb
        der Liste aus parrent und child angibt und dann diesen Zustand zurueckgibt.
        0 - Gibt den Zustand in parrent zurueck
        1...n Gibt den x. Zustand aus child zurueck.
        @name Gibt den Zustand mit dem Namen name zurueck.
        Oder """

        # Wandle nicht numerische Kommandos in numerische um
        if index_child and index_child[0] == "@":                              # @ = Suche index nach Namen
            index_child = self.position_zustand_in_child_mit_namen(index_child[1:])

        # Veraerbeite regulaere Kommandos
        if index_child and int(index_child[0]) == 0:                           # 0 = Zurueck zum vorherigen Zustand
            return ZustandReturnValue(self.parent, lambda: None, tuple())
        return ZustandReturnValue(
            zustand=replace(self.child[int(index_child) - 1], parent=self), cmd=lambda: None, args=tuple()
        ) if index_child else ZustandReturnValue(self, lambda: None, tuple())  # Leere String => self als neuer Zustand

    def update_zeit(self, neue_zeit_im_iso_format: str):
        return replace(self, aktuelle_zeit=neue_zeit_im_iso_format)


@dataclass(frozen=True)
class ZustandENDE(Zustand):
    titel: str = field(default='ENDE')
    beschreibung: str = field(default='Beende Programm')


@dataclass(frozen=True)
class ZustandBoxinfo(Zustand):
    info: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)
    aktuelle_frageeinheit: str = ''
    box_titel: str = ''
    titel: str = 'Zustand 2'
    beschreibung: str = 'Zustand 2, Zeigt die Boxinfos der aktuellen Box an.'
    child: list[Zustand] = field(default_factory=list)
    kommandos: list[str] = field(default=("+", "-", "="))

    def parse_user_eingabe(self, cmd_str: list[str]) -> tuple[str, tuple]:
        print(f" cmdParser Zustand: {self.__class__.__name__} - {cmd_str = }")
        index_aktuelle_frage = list(self.info.keys()).index(self.aktuelle_frageeinheit)
        match cmd_str:
            case ['=', *frage_einheit]:
                return "CmdStartChangeAktuellenFrageeinheit", (''.join(frage_einheit),)
            case ['+', *wert]:
                neuer_index = (index_aktuelle_frage + int(''.join(wert))) % len(self.info) % len(self.info)
                neue_frageeinheit = list(self.info.keys())[neuer_index]
                return "CmdStartChangeAktuellenFrageeinheit", (neue_frageeinheit,)
            case ['-', *wert]:
                neuer_index = (index_aktuelle_frage - int(''.join(wert))) % len(self.info) % len(self.info)
                neue_frageeinheit = list(self.info.keys())[neuer_index]
                return "CmdStartChangeAktuellenFrageeinheit", (neue_frageeinheit,)
        return super().parse_user_eingabe(cmd_str)   # Liefert tuple("", tuple())

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        """Veraendert die aktuelle Frageeinheit.
        + -> Naechste Frageeinheit.
        - -> Vorherige Frageeinheit.
        = + String -> Frageeinheit mit Namen"""
        if index_child == '':
            return ZustandReturnValue(self, lambda: None, tuple())
        # Bei Veranderungen rufe die Funktion update_modell_aktueller_index() mit dem neuen Index im Controller auf.
        if index_child[0] in ['+', '-']:
            index_aktuelle_frage = list(self.info.keys()).index(self.aktuelle_frageeinheit)
            neuer_index = (index_aktuelle_frage + int(index_child)) % len(self.info)
            neue_frageeinheit = list(self.info.keys())[neuer_index]
            return ZustandReturnValue(replace(self, aktuelle_frageeinheit=neue_frageeinheit),
                                      cast(Callable, 'update_modell_aktuelle_frageeinheit'),
                                      (neue_frageeinheit,))
        if "=" == index_child[0]:
            return ZustandReturnValue(replace(self, aktuelle_frageeinheit=index_child[1:]),
                                      cast(Callable, 'update_modell_aktuelle_frageeinheit'),
                                      (index_child[1:],))
        return super().verarbeite_userinput(index_child)
