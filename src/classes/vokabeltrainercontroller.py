from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
import datetime
import time
from typing import Callable, Type, cast, TYPE_CHECKING

from src.classes.eventmanager import EventTyp
from src.classes.lernuhr import Lernuhr
from src.classes.zustand import (Zustand, ZustandStart, ZustandENDE,
                                 ZustandBoxinfo, ZustandVeraenderLernuhr, ZustandReturnValue)
from src.classes.infomanager import InfoManager

if TYPE_CHECKING:
    from src.classes.eventmanager import EventManager
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.classes.zustandsbeobachter import ObserverManager
    from src.classes.vokabelkarte import Vokabelkarte


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view_observer: ObserverManager,
                 event_manager: EventManager):
        self.modell: VokabeltrainerModell = modell
        self.info_manager: InfoManager = InfoManager()
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
                                   'child': (self.buildZustandBoxinfo(ZustandBoxinfo()),
                                             self.buildZustandVeraenderLernuhr(ZustandVeraenderLernuhr()),
                                             ZustandENDE())})

    def buildZustandBoxinfo(self, zustand: ZustandBoxinfo) -> ZustandBoxinfo:
        return replace(zustand, **{'info': self.info_manager.boxen_als_number_dict()[self.modell.index_aktuelle_box],
                                   'aktuelle_frageeinheit': self.modell.aktuelle_box().aktuelle_frage.__name__,
                                   'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                   'box_titel': self.modell.aktuelle_box().titel,
                                   'child': (self.buildZustandVeraenderLernuhr(ZustandVeraenderLernuhr()),)})

    def buildZustandVeraenderLernuhr(self, zustand: ZustandVeraenderLernuhr) -> ZustandVeraenderLernuhr:
        if zustand.aktuelle_zeit == '':
            return replace(zustand, **{'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                       'neue_uhr': self.uhr})
        return replace(zustand, neue_uhr=self.uhr)

    def update_uhr(self, neue_uhr: Lernuhr) -> None:
        print(f"update_uhr vorher: {self.uhr == neue_uhr = }")  # TODO Debug entfernen
        self.uhr = neue_uhr
        print(f"update_uhr nachher: {self.uhr == neue_uhr = }")  # TODO Debug entfernen

    def update_modell_aktueller_index(self, neuer_index: int) -> None:
        self.modell = replace(self.modell, index_aktuelle_box=neuer_index)

    def update_vokabelkarte_statisitk(self, karte: tuple[Vokabelkarte, Callable[[int], Vokabelkarte]]) -> None:
        """Ruft die Funktion zum Erstellen und Hinzufuegen der Antwort mit der aktuellen Zeit auf und ersetzt dann
        die alte Karte durch die neue Karte im repository."""
        alte_karte, funktion = karte
        neue_karte = funktion(self.uhr.now(Lernuhr.echte_zeit()))
        self.modell.vokabelkarten.replace_karte(alte_karte, neue_karte)

    def execute_kommando(self, kommando_string: str) -> Zustand:
        # TODO Scheibe funktion self.execute_kommando_interpreter(zustand, interpreter, cmd
        #   das systemcommands des vokabeltrainers mit uebergibt.

        commands = {'update_uhr': self.update_uhr,
                    'update_modell_aktueller_index': self.update_modell_aktueller_index,
                    'update_vokabelkarte_statisitk': self.update_vokabelkarte_statisitk}

        print(f"execute_kommando: {kommando_string = }")  # TODO Debug entfernen
        result: ZustandReturnValue = self.aktueller_zustand.verarbeite_userinput(kommando_string)
        print(f"execute_kommando: {result = }")  # TODO Debug entfernen
        if cmd := commands.get(cast(str, result.cmd), False):
            cmd(*result.args)
        return replace(result.zustand,      # Aktualisiere alle Zustaende in child des result-Zustands
                       child=[self.update_zustand(child_zustand) for child_zustand in result.zustand.child])

    def update_zustand(self, alter_zustand: Zustand) -> Zustand:
        """Ruft die builder()-Funktionen auf, die die Zustaende mit den aktuellen Werten neu bauen.
        Die Zuordnung der Zustaende zu den buildern wird in der service_liste festgelegt."""
        service_liste: dict[Type[Zustand], Callable] = {
            ZustandVeraenderLernuhr: self.buildZustandVeraenderLernuhr,
            ZustandStart: self.buildZustandStart,
            ZustandBoxinfo: self.buildZustandBoxinfo
        }
        func = service_liste.get(alter_zustand.__class__, lambda x: x)
        return func(alter_zustand)

    def setze_cmd_str(self, cmd_str) -> None:
        self.cmd = cmd_str
        self.aktueller_zustand = self.execute_kommando(self.cmd[1:])
        self.event_manager.publish_event(EventTyp.KOMMANDO_EXECUTED, self.aktueller_zustand)
        self.cmd = ''

    def programm_loop(self):
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = ZustandStart(liste=self.modell.vokabelboxen.titel_aller_vokabelboxen(),
                                              aktueller_index=self.modell.index_aktuelle_box,
                                              aktuelle_zeit=self.uhr.as_iso_format(Lernuhr.echte_zeit()))
        self.modell.vokabelkarten.laden()
        # TODO Erstellen des InfoManagers blockiert das System, so dass der aktuelle zustand nicht gesetzt ist
        #   und Flaskview Fehlermeldungen (KeyError) beim Abrufen der Zeit ausgibt (siehe get_Routen in flaskview.py).
        self.info_manager = InfoManager.factory(liste_der_boxen=self.modell.vokabelboxen.vokabelboxen,
                                                liste_der_karten=self.modell.vokabelkarten.vokabelkarten
                                                ).erzeuge_alle_infos(self.uhr.now(Lernuhr.echte_zeit()))
        print(f"Beginne mit der Arbeit. { self.info_manager.boxen_als_number_dict()[40] = }")

        self.aktueller_zustand = self.buildZustandStart(ZustandStart())
        self.view_observer.views_updaten(self.aktueller_zustand, Lernuhr.echte_zeit())
        self.view_observer.views_rendern()

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            self.aktueller_zustand = self.aktueller_zustand.update_zeit(self.uhr.as_iso_format(Lernuhr.echte_zeit()))
            self.event_manager.publish_event(EventTyp.LOOP_ENDE, self.aktueller_zustand)
            time.sleep(0.25)

        self.event_manager.publish_event(EventTyp.PROGRAMM_BENDET, self.aktueller_zustand)
