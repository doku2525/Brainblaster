from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Callable, NamedTuple, TYPE_CHECKING, cast


class ZustandReturnValue(NamedTuple):
    zustand: Zustand
    kommando: str
    args: tuple


@dataclass(frozen=True)
class Zustand(ABC):
    beschreibung: str = field(default_factory=str)
    titel: str = field(default_factory=str)
    kommandos: list[str] = field(default_factory=list)
    aktuelle_zeit: str = field(default_factory=str)

    def parse_user_eingabe(self, cmd_str: list[str]) -> tuple[str, tuple]:
        """Liest cmd-String und liefert Tuple mit KommandoString und args"""
        return "", tuple()   # Abstarkte Klasse, deshalb gibt es keine Kommandos

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
    # child: list[Zustand] = field(default_factory=list)
    kommandos: list[str] = field(default=("+", "-", "="))

    def parse_user_eingabe(self, cmd_str: list[str]) -> tuple[str, tuple]:
        print(f" cmdParser Zustand: {self.__class__.__name__} - {cmd_str = }")
        index_aktuelle_frage = list(self.info.keys()).index(self.aktuelle_frageeinheit)
        match cmd_str:
            case ['=', *frage_einheit]:
                return "CmdStartChangeAktuelleFrageeinheit", (''.join(frage_einheit),)
            case ['+', *wert]:
                neuer_index = (index_aktuelle_frage + int(''.join(wert))) % len(self.info) % len(self.info)
                neue_frageeinheit = list(self.info.keys())[neuer_index]
                return "CmdStartChangeAktuelleFrageeinheit", (neue_frageeinheit,)
            case ['-', *wert]:
                neuer_index = (index_aktuelle_frage - int(''.join(wert))) % len(self.info) % len(self.info)
                neue_frageeinheit = list(self.info.keys())[neuer_index]
                return "CmdStartChangeAktuelleFrageeinheit", (neue_frageeinheit,)
        return super().parse_user_eingabe(cmd_str)   # Liefert tuple("", tuple())
