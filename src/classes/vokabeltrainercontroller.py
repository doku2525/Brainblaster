from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
import datetime
import time
from typing import Type, cast, TYPE_CHECKING

from src.classes.eventmanager import EventTyp
from src.classes.lernuhr import Lernuhr
from src.classes.zustand import Zustand, ZustandStart, ZustandENDE, ZustandVeraenderLernuhr, ZustandReturnValue

if TYPE_CHECKING:
    from src.classes.eventmanager import EventManager
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.classes.zustandsbeobachter import ObserverManager


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view_observer: ObserverManager,
                 event_manager: EventManager):
        self.modell: VokabeltrainerModell = modell
        self.uhr: Lernuhr = uhr
        self.aktueller_zustand: Zustand | None = None
        self.view_observer: ObserverManager = view_observer
        self.event_manager: EventManager = event_manager
        self.cmd: str = ''

        # Subscribe Events
        self.event_manager.subscribe(EventTyp.NEUES_KOMMANDO, self.setze_cmd_str)
        self.event_manager.subscribe(EventTyp.KOMMANDO_EXECUTED,
                                     lambda zustand: self.view_observer.views_updaten(zustand, Lernuhr.echte_zeit()))
        self.event_manager.subscribe(EventTyp.LOOP_ENDE,
                                     lambda zustand: self.view_observer.views_updaten(zustand, Lernuhr.echte_zeit()))
        self.event_manager.subscribe(EventTyp.KOMMANDO_EXECUTED,
                                     lambda zustand: self.view_observer.views_rendern())
        self.event_manager.subscribe(EventTyp.PROGRAMM_BENDET,
                                     lambda zustand: self.view_observer.views_rendern())

    # TODO Problem mit neuen Zustaenden.
    #   Jeder Zustand bekommt create-Klassenvariable. diese wird als cmd uebergeben. ZustandX().creeate.
    #   self.aktuellerZustand ist dann None. args ist dann die Funktion zum bauen der Argumente.
    #   f() -> dict. So dass dann cmd(**args()) aufgerufen wird, wenn aktueller_zustand None ist

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
        print(f"update_uhr vorher: {self.uhr == neue_uhr = }")  # TODO Debug entfernen
        self.uhr = neue_uhr
        print(f"update_uhr nachher: {self.uhr == neue_uhr = }")  # TODO Debug entfernen

    def execute_kommando(self, kommando_string: str) -> Zustand:
        # TODO Scheibe funktion self.execute_kommando_interpreter(zustand, interpreter, cmd
        #   das systemcommands des vokabeltrainers mit uebergibt.

        commands = {'update_uhr': self.update_uhr}
        print(f"execute_kommando: {kommando_string = }")  # TODO Debug entfernen
        result = self.aktueller_zustand.verarbeite_userinput(kommando_string)
        print(f"execute_kommando: {result = }")  # TODO Debug entfernen
        if cmd := commands.get(result.cmd, False):
            cmd(*result.args)
        return replace(result.zustand,      # Aktualisiere alle Zustaende in child des result-Zustands
                       child=[self.update_zustand(child_zustand) for child_zustand in result.zustand.child])

    def update_zustand(self, alter_zustand: Zustand) -> Zustand:
        """Ruft die builder()-Funktionen auf, die die Zustaende mit den aktuellen Werten neu bauen.
        Die Zuordnung der Zustaende zu den buildern wird in der service_liste festgelegt."""
        service_liste = {
            ZustandVeraenderLernuhr: self.buildZustandVeraenderLernuhr,
            ZustandStart: self.buildZustandStart
        }
        func = service_liste.get(alter_zustand.__class__, lambda x: x)
        return func(alter_zustand)

    def setze_cmd_str(self, cmd_str) -> None:
        self.cmd = cmd_str
        self.aktueller_zustand = self.execute_kommando(self.cmd[1:])
        self.event_manager.publish_event(EventTyp.KOMMANDO_EXECUTED, self.aktueller_zustand)
        self.cmd = ''

    def programm_loop(self):
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = self.buildZustandStart(ZustandStart())
        self.view_observer.views_updaten(self.aktueller_zustand, Lernuhr.echte_zeit())
        self.view_observer.views_rendern()

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            self.aktueller_zustand = self.aktueller_zustand.update_zeit(self.uhr.as_iso_format(Lernuhr.echte_zeit()))
            self.event_manager.publish_event(EventTyp.LOOP_ENDE, self.aktueller_zustand)
            time.sleep(0.25)

        self.event_manager.publish_event(EventTyp.PROGRAMM_BENDET, self.aktueller_zustand)
