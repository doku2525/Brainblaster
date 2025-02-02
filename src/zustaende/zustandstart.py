from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Callable, TYPE_CHECKING, cast

from src.zustaende.zustand import ZustandReturnValue, Zustand, ZustandENDE


@dataclass(frozen=True)
class ZustandStart(Zustand):
    liste: list[str] = field(default_factory=list)
    aktueller_index: int = 0
    titel: str = 'Zustand 1'
    beschreibung: str = 'Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.'
    kommandos: list[str] = field(default=("+", "-", "=", "s"))

    def parse_user_eingabe(self, cmd_str: list[str]) -> tuple[str, tuple]:
        print(f" cmdParser Zustand: {self.__class__.__name__} - {cmd_str = }")
        match cmd_str:
            case ['=', *wert]:
                neuer_index = min(len(self.liste) - 1, max(0, int(''.join(wert))))
                return "CmdStartChangeAktuellenIndex", (neuer_index,)
            case ['+', *wert]:
                neuer_index = min(len(self.liste) - 1, self.aktueller_index + int(''.join(wert)))
                return "CmdStartChangeAktuellenIndex", (neuer_index,)
            case ['-', *wert]:
                neuer_index = max(0, self.aktueller_index - int(''.join(wert)))
                return "CmdStartChangeAktuellenIndex", (neuer_index,)
            case ['s']: return 'CmdSpeicherRepositories', tuple()
        return super().parse_user_eingabe(cmd_str)   # Liefert tuple("", tuple()) aus Zustand
