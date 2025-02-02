from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Callable, TYPE_CHECKING

from src.classes.vokabeltrainercontroller import VokabeltrainerController


class Kommando(ABC):
    def execute(self, controller: VokabeltrainerController) -> VokabeltrainerController:
        ...


class CmdUpdateUhr(Kommando):
    def execute(self, controller: VokabeltrainerController) -> Callable[[Any], VokabeltrainerController]:
        # Speicher die Werte
        raise NotImplementedError


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


class CmdStartChangeAktuellenFrageeinheit(Kommando):
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
