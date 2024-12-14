from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable



@dataclass(frozen=True)
class InterpreterKommando:
    beschreibung: str = field(default_factory=str)
    cmd: Callable = field(default_factory=Callable)
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)


class KommandoInterpreter(ABC):

    @property
    @abstractmethod
    def kommandos(self) -> dict:
        return {}


class KommandoInterpreterVeraenderLernuhr(KommandoInterpreter):

    @property
    def kommandos(self) -> dict:
        return {
            's': InterpreterKommando(
                beschreibung='Veraender die start_zeit.' +
                             's=24-12-01 12:00:00, s+1T|H|M, s-1T|H|M T=Tage, H=Stunden, M=Minuten'),
            'k': InterpreterKommando(
                beschreibung='Veraender die kalkulations_zeit.' +
                             'k=24-12-01 12:00:00, k+1T|H|M, k-1T|H|M T=Tage, H=Stunden, M=Minuten'),
            't': InterpreterKommando(beschreibung='Veraender das Tempo. t1.0'),
            'z': InterpreterKommando(beschreibung='Veraender den Modus. ze = ECHTE, zl = LAEUFT, zp = PAUSE')
            # TODO Pause start pause ende
            # TODO Rest
        }