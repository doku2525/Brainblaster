from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Callable, Protocol, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from src.classes.zustand import Zustand


class Beobachter(Protocol):

    def update(self, data: dict) -> None | Beobachter:
        ...


@dataclass(frozen=True)
class ObserverManager:
    registrierte_view_klassen: dict[Type[Beobachter], dict[Callable, Callable]] = field(default_factory=dict)
    beobachter: list[Beobachter] = field(default_factory=list)

    def registriere_mapping(self, view: Beobachter, mediator_funktion: Callable,
                            observer_funktion: Callabel) -> ObserverManager:
        result = replace(self,
                         registrierte_view_klassen=self.registrierte_view_klassen | {
                             view.__class__: {observer_funktion.__func__.__name__: mediator_funktion}
                         })
        return result.view_anmelden(view)

    def view_anmelden(self, neuer_beobachter: Beobachter) -> ObserverManager:
        return replace(self, beobachter=self.beobachter + [neuer_beobachter])

    def view_abmelden(self, beobachter: Beobachter) -> ObserverManager:
        return replace(self, beobachter=[observer for observer in self.beobachter if observer != beobachter])

    def suche_cmd(self, view_obj: Beobachter,
                  observer_funktion: Callable[[...], ObserverManager],
                  default_result: Callable[[Zustand, int], dict]) -> Callable[[Zustand, int], dict]:
        """ Helper-Funktion
        Suche nach der entsprechend Konverterfunktion des ZustandsMediators fuer die View
        Falls keine Funktion gefunden wird, liefer eine Funktion, die nur eine leere Liste liefert. """
        return self.registrierte_view_klassen.get(  # Suche(get) in self.registrierte_view_klassen
            view_obj.__class__, {}                  # erst nach der View-Klasse (1. Ebene)
        ).get(observer_funktion.__func__.__name__ if hasattr(observer_funktion, '__func__') else None,  # z.B. lambda:
              default_result)                       # dann suche(get) nach der Observer-Funktion und liefer den Value

    def views_updaten(self, zustand: Zustand, zeit_in_mills: int,
                      default_result: Callable[[Zustand, int], dict] = lambda x, t: {}) -> ObserverManager:
        """ Rufe die update()-Funktion der angemeldeten Beobachter (Views).
                Konvertiere die args mit der in registrierte_view_klassen gespeicherten Funktion"""
        [observer.update(
            self.suche_cmd(observer, self.views_updaten, default_result)(zustand, zeit_in_mills))
         for observer in self.beobachter]
        return self

    def views_rendern(self) -> ObserverManager:
        """ Rufe die render()-Funktion der angemeldeten Beobachter (Views). """
        [observer.render() for observer in self.beobachter if hasattr(observer, 'render')]
        return self
