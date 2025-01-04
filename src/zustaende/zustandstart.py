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
    child: list[Zustand] = field(default=(ZustandENDE(),))
    kommandos: list[str] = field(default=("+", "-", "=", "s"))

    def __post_init__(self):
        object.__setattr__(self, 'parent', None)    # Der StartZustand hat kein parent!!!

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        """Verarbeite den userinput"""
        if index_child == '':
            return ZustandReturnValue(self, lambda: None, tuple())
        # Bei Veranderungen rufe die Funktion update_modell_aktueller_index() mit dem neuen Index im Controller auf.
        if "+" == index_child[0]:
            neuer_index = min(len(self.liste)-1, self.aktueller_index + int(index_child[1:]))
            return ZustandReturnValue(replace(self, aktueller_index=neuer_index),
                                      cast(Callable, 'update_modell_aktueller_index'),
                                      (neuer_index,))
        if "-" == index_child[0]:
            neuer_index = max(0, self.aktueller_index - int(index_child[1:]))
            return ZustandReturnValue(replace(self, aktueller_index=neuer_index),
                                      cast(Callable, 'update_modell_aktueller_index'),
                                      (neuer_index,))
        if "=" == index_child[0]:
            neuer_index = min(len(self.liste)-1, max(0, int(index_child[1:])))
            return ZustandReturnValue(replace(self, aktueller_index=neuer_index),
                                      cast(Callable, 'update_modell_aktueller_index'),
                                      (neuer_index,))
        if "s" == index_child[0]:
            return ZustandReturnValue(self, cast(Callable, 'speicher_daten_in_dateien'), tuple())
        return super().verarbeite_userinput(index_child)
