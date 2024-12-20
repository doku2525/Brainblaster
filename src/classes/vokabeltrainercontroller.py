from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
import datetime
import time
from typing import Type, cast, TYPE_CHECKING

from src.classes.lernuhr import Lernuhr
from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.zustand import Zustand, ZustandStart, ZustandENDE, ZustandVeraenderLernuhr, ZustandReturnValue
from src.classes.zustandsmediator import ZustandsMediator
from src.views.consoleview import ConsoleView

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.views.flaskview import FlaskView


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view: FlaskView):
        self.modell = modell
        self.uhr = uhr
        self.aktueller_zustand = None
        self.view = view
        self.view_console = ConsoleView()

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
        return replace(zustand, neue_uhr=self.uhr)

    def update_uhr(self, neue_uhr: Lernuhr) -> None:
        print(f"update_uhr vorher: {self.uhr == neue_uhr = }")
        self.uhr = neue_uhr
        print(f"update_uhr nachher: {self.uhr == neue_uhr = }")

    def execute_kommando(self, kommando_string: str) -> Zustand:
        commands = {'update_uhr': self.update_uhr}
        print(f"execute_kommando: {kommando_string = }")
        result = self.aktueller_zustand.verarbeite_userinput(kommando_string)
        print(f"execute_kommando: {result = }")
        if cmd := commands.get(result.cmd, False):
            cmd(*result.args)
        return replace(result.zustand,
                       child=[self.update_zustand(child_zustand) for child_zustand in result.zustand.child])

    def update_zustand(self, alter_zustand: Zustand) -> Zustand:
        service_liste = {
            ZustandVeraenderLernuhr: self.buildZustandVeraenderLernuhr,
            ZustandStart: self.buildZustandStart
        }
        func = service_liste.get(cast(Type[Zustand], alter_zustand.__class__), lambda x: x)
        return func(alter_zustand)

    def programm_loop(self):
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = self.buildZustandStart(ZustandStart())
        # TODO Hier den Observer aufrufen und alle registrierten View die Nachricht updaten() schicken
        self.view.data = ZustandsMediator().zustand_to_flaskview_data(self.aktueller_zustand)   # In FlaskView durch updaten() zuweisen
        self.view_console = self.view_console.update(
            ZustandsMediator().zustand_to_consoleview_data(self.aktueller_zustand))
        self.view_console.render()

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            if self.view.cmd and self.view.cmd[0] == 'c':
                # Scheibe funktion self.execute_kommando_interpreter(zustand, interpreter, cmd
                #   das systemcommands des vokabeltrainers mit uebergibt.
                self.aktueller_zustand = self.execute_kommando(self.view.cmd[1:])
                # TODO Problem mit neuen Zustaenden.
                #   Jeder Zustand bekommt create-Klassenvariable. diese wird als cmd uebergeben. ZustandX().creeate.
                #   self.aktuellerZustand ist dann None. args ist dann die Funktion zum bauen der Argumente.
                #   f() -> dict. So dass dann cmd(**args()) aufgerufen wird, wenn aktueller_zustand None ist

                self.view.data = ZustandsMediator().zustand_to_flaskview_data(self.aktueller_zustand)
                self.view_console = self.view_console.update(
                    ZustandsMediator().zustand_to_consoleview_data(self.aktueller_zustand))
                self.view.cmd = None
                # Bzw. spaeter dann wenn der Observer in Zustand integriert wurde, aktueller_zustand.render() aufrufen.
                self.view_console.render()

            self.aktueller_zustand = self.aktueller_zustand.update_zeit(self.uhr.as_iso_format(Lernuhr.echte_zeit()))
            self.view.data = ZustandsMediator().zustand_to_flaskview_data(self.aktueller_zustand)
            time.sleep(0.25)

        print(self.aktueller_zustand.info_text_konsole())
