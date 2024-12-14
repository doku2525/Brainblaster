from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
import datetime
import time
from typing import TYPE_CHECKING

from src.classes.lernuhr import Lernuhr
from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.zustand import Zustand, ZustandStart, ZustandENDE, ZustandVeraenderLernuhr, ZustandReturnValue

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.views.flaskview import FlaskView


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view: FlaskView):
        self.modell = modell
        self.uhr = uhr
        self.aktueller_zustand = None
        self.view = view

    def buildZustandStart(self, zustand: ZustandStart) -> ZustandStart:
        return replace(zustand, **{'liste': self.modell.vokabelboxen.titel_aller_vokabelboxen(),
                                   'aktueller_index': self.modell.index_aktuelle_box,
                                   'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                   'child': (self.buildZustandVeraenderLernuhr(ZustandVeraenderLernuhr()),
                                             ZustandENDE())})

    def buildZustandVeraenderLernuhr(self, zustand: ZustandVeraenderLernuhr) -> ZustandVeraenderLernuhr:
        if zustand.aktuelle_zeit == '':
            return replace(zustand, **{'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                       'neue_uhr': self.uhr})
        return zustand

    def update_uhr(self, neue_uhr: Lernuhr) -> None:
        self.uhr = neue_uhr

    def execute_kommando(self, kommando_string: str) -> Zustand:
        commands = {'update_uhr': self.update_uhr}
        result = self.aktueller_zustand.verarbeite_userinput(kommando_string)
        if cmd := commands.get(result.cmd, False):
            cmd(*result.args)
        return result.zustand

    def programm_loop(self):
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = self.buildZustandStart(ZustandStart())
        self.view.data = self.aktueller_zustand.data
        print(self.aktueller_zustand.daten_text_konsole())
        print(self.aktueller_zustand.info_text_konsole())

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            if self.view.cmd and self.view.cmd[0] == 'c':
                # Scheibe funktion self.execute_kommando_interpreter(zustand, interpreter, cmd
                #   das systemcommands des vokabeltrainers mit uebergibt.
                self.aktueller_zustand = self.execute_kommando(self.view.cmd[1:])
                # TODO Problem mit neuen Zustaenden.
                #   Jeder Zustand bekommt create-Klassenvariable. diese wird als cmd uebergeben. ZustandX().creeate.
                #   self.aktuellerZustand ist dann None. args ist dann die Funktion zum bauen der Argumente.
                #   f() -> dict. So dass dann cmd(**args()) aufgerufen wird, wenn aktueller_zustand None ist

                print(f"AktuellerZustand {self.aktueller_zustand}")
                self.view.data = self.aktueller_zustand.data
                self.view.cmd = None
                print(self.aktueller_zustand.daten_text_konsole())
                print(self.aktueller_zustand.info_text_konsole())
            self.aktueller_zustand = self.aktueller_zustand.update_zeit(self.uhr.as_iso_format(Lernuhr.echte_zeit()))
            self.view.data = self.aktueller_zustand.data
            time.sleep(0.25)

        print(self.aktueller_zustand.info_text_konsole())
