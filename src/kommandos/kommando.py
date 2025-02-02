from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Callable, TYPE_CHECKING

from src.classes.vokabeltrainercontroller import VokabeltrainerController
if TYPE_CHECKING:
    from src.zustaende.zustand import Zustand
    from src.classes.lernuhr import Lernuhr


class Kommando(ABC):
    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        """Liefert eine Funktion, die dann die an sie uebergebenen Argumente auf den Controller anwendet."""
        ...


class CmdErsetzeAktuellenZustand(Kommando):

    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        """
        Ersetze den aktuellen Zustand durch den als Argument uebergebenen Zustand.
        Das Kommando wird vor allem von Lernuhr benoetigt
        """
        def funktion(zustand: Zustand) -> VokabeltrainerController:
            controller.aktueller_zustand = zustand
            return controller
        return funktion


class CmdErsetzeLernuhr(Kommando):
    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        # Speicher die Werte
        def funktion(neue_uhr: Lernuhr) -> VokabeltrainerController:
            controller.update_uhr(neue_uhr)
            return controller
        return funktion


class CmdStartChangeAktuellenIndex(Kommando):
    def execute(
            self,
            controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        def funktion(neuer_index: int = None) -> VokabeltrainerController:
            if neuer_index is None:
                return controller
            controller.aktueller_zustand = replace(controller.aktueller_zustand, aktueller_index=neuer_index)
            controller.modell = replace(controller.modell, index_aktuelle_box=neuer_index)
            return controller
        return funktion


class CmdStartChangeAktuelleFrageeinheit(Kommando):
    def execute(
            self,
            controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        def funktion(neue_frageeinheit: str) -> VokabeltrainerController:
            """Veraender die aktuelle_frage in der aktuellen Vokabelbox"""
            neue_frage = [frageeinheit
                          for frageeinheit
                          in controller.modell.aktuelle_box().verfuegbare_frageeinheiten()
                          if frageeinheit.__name__ == neue_frageeinheit]
            neue_box = replace(controller.modell.aktuelle_box(), aktuelle_frage=neue_frage[0])
            controller.aktueller_zustand = replace(controller.aktueller_zustand,
                                                   aktuelle_frageeinheit=neue_frageeinheit)
            controller.modell.vokabelboxen.vokabelboxen[controller.modell.index_aktuelle_box] = neue_box
            return controller
        return funktion


class CmdSpeicherRepositories(Kommando):
    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        def funktion(irgendwas: Any = None) -> VokabeltrainerController:
            controller.speicher_daten_in_dateien()
            return controller
        return funktion


class CmdTestErgebnis(Kommando):
    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        def funktion(*args):
            zustand, karten_tupel = args
            if karten_tupel:
                controller.update_vokabelkarte_statistik(karten_tupel)
            controller.aktueller_zustand = zustand
            return controller
        return funktion
