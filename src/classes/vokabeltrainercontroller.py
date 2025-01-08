from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import replace
import logging
import time
from typing import Callable, cast, TYPE_CHECKING
from threading import Thread
import threading

from src.classes.configurator import config
from src.classes.eventmanager import EventTyp
from src.classes.lernuhr import Lernuhr
from src.classes.infomanager import InfoManager
from src.zustaende.zustandsfactory import ZustandsFactory
import src.utils.utils_io as u_io
import src.utils.utils_performancelogger as u_log

if TYPE_CHECKING:
    from src.classes.eventmanager import EventManager
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.classes.zustandsbeobachter import ObserverManager
    from src.classes.vokabelkarte import Vokabelkarte
    from src.zustaende.zustand import Zustand


# Initializiere Logger
logger = u_log.ZeitLogger.create(f"{config.log_pfad}performance.log", __name__)
logger.starte_logging()


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
        self.info_manager_lock = None       # Lock fuer Threads zum Updaten des Infomanagers

        # Subscribe Events
        logger.start()
        self.event_manager.subscribe(EventTyp.NEUES_KOMMANDO, self.setze_cmd_str)
        self.event_manager.subscribe(EventTyp.KOMMANDO_EXECUTED,
                                     lambda zustand: self.view_observer.views_updaten(zustand, Lernuhr.echte_zeit()))
        self.event_manager.subscribe(EventTyp.LOOP_ENDE,
                                     lambda zustand: self.view_observer.views_updaten(zustand, Lernuhr.echte_zeit()))
        self.event_manager.subscribe(EventTyp.KOMMANDO_EXECUTED,
                                     lambda zustand: self.view_observer.views_rendern())
        self.event_manager.subscribe(EventTyp.PROGRAMM_BENDET,
                                     lambda zustand: self.view_observer.views_rendern())
        logger.fertig("Subscribe Events")

    # Definiere Systemkommandos, die von den Zustaenden aufgerufen werden koennen.
    #  Jede Funktion muss im command-Dictionary der Funktion execute_kommando() registriert werden
    def update_uhr(self, neue_uhr: Lernuhr) -> None:
        self.uhr = neue_uhr
        logger.start()
        self.info_manager = self.info_manager.erzeuge_alle_infos(self.uhr.now(Lernuhr.echte_zeit()))
        logger.fertig("\tupdate_uhr -> info_manager.erzeuge_alle_infos()")

    def update_modell_aktueller_index(self, neuer_index: int) -> None:
        self.modell = replace(self.modell, index_aktuelle_box=neuer_index)

    def update_modell_aktuelle_frageeinheit(self, neue_frageeinheit: str) -> None:
        """Veraender die aktuelle_frage in der aktuellen Vokabelbox"""
        neue_frage = [frageeinheit
                      for frageeinheit
                      in self.modell.aktuelle_box().verfuegbare_frageeinheiten()
                      if frageeinheit.__name__ == neue_frageeinheit]
        neue_box = replace(self.modell.aktuelle_box(), aktuelle_frage=neue_frage[0])
        self.modell.vokabelboxen.vokabelboxen[self.modell.index_aktuelle_box] = neue_box
        self.aktueller_zustand = (ZustandsFactory(self.modell, self.uhr, self.info_manager).
                                  update_frageeinheit(self.aktueller_zustand))

    def update_vokabelkarte_statistik(self, karte: tuple[Vokabelkarte, Callable[[int], Vokabelkarte]]) -> None:
        """Ruft die Funktion zum Erstellen und Hinzufuegen der Antwort mit der aktuellen Zeit auf und ersetzt dann
        die alte Karte durch die neue Karte im repository."""
        alte_karte, funktion = karte
        neue_karte = funktion(self.uhr.now(Lernuhr.echte_zeit()))
        logger.start()
        self.modell.vokabelkarten.replace_karte(alte_karte, neue_karte)
        logger.fertig(f"\tupdate_vokabelkarte_statistik->self.modell.vokabelkarten.replace_karte")
        logger.start(f"\tupdate_vokabelkarte_statistik Thread info_manager.update_infos_fuer_karte")
        self.info_manager_lock = threading.Lock()

        def update_info_in_thread():
            """Urspruengliche Funktion in Funktion verpackt, die vom Thread gestartet wird"""
            logger.start(f"\t\tupdate_vokabelkarte_statistik -> update_info_in_thread")
            with self.info_manager_lock:
                self.info_manager = self.info_manager.update_infos_fuer_karte(alte_karte,
                                                                              neue_karte,
                                                                              self.uhr.now(Lernuhr.echte_zeit()))
            logger.fertig(f"\t\tupdate_vokabelkarte_statistik -> update_info_in_thread")

        thread = threading.Thread(target=update_info_in_thread)
        thread.start()
        logger.fertig(f"\tupdate_vokabelkarte_statistik -> self.info_manager.update_infos_fuer_karte")

    def speicher_daten_in_dateien(self):
        def speicher_prozess():
            logger.start()
            uhr_datei = f"{config.daten_pfad}{config.uhr_dateiname}"
            config_datei = f"{config.daten_pfad}{config.config_dateiname}"
            dateiliste = [self.modell.vokabelkarten.dateiname,
                          self.modell.vokabelboxen.dateiname,
                          uhr_datei,
                          config_datei]
            prozess = u_io.schreibe_backup(dateiliste, config.backup_pfad)
            prozess.join()
            self.modell.vokabelkarten.speichern()
            self.modell.vokabelboxen.speichern()
            config.speicher()
            u_io.speicher_in_jsondatei(self.uhr.as_iso_dict(), uhr_datei)
            logger.fertig(f"\t\tspeicher_daten_in_dateien -> speicher_prozess")

        logger.start()
        speicher_thread = Thread(target=speicher_prozess)
        speicher_thread.start()
        logger.fertig(f"\tspeicher_daten_in_dateien -> thread starten")

    # Funktionen zum Ausfuehren und aktuallisieren des Systems
    def execute_kommando(self, kommando_string: str) -> Zustand:
        # TODO Scheibe funktion self.execute_kommando_interpreter(zustand, interpreter, cmd
        #   das systemcommands des vokabeltrainers mit uebergibt.
        commands = {'update_uhr': self.update_uhr,
                    'update_modell_aktueller_index': self.update_modell_aktueller_index,
                    'update_vokabelkarte_statistik': self.update_vokabelkarte_statistik,
                    'update_modell_aktuelle_frageeinheit': self.update_modell_aktuelle_frageeinheit,
                    'speicher_daten_in_dateien': self.speicher_daten_in_dateien}

        print(f"execute_kommando: {kommando_string = }")  # TODO Debug entfernen
        result: ZustandReturnValue = self.aktueller_zustand.verarbeite_userinput(kommando_string)
        print(f"execute_kommando: {result.cmd = }")  # TODO Debug entfernen
        if cmd := commands.get(cast(str, result.cmd), False):
            cmd(*result.args)
        # Gib den aktuallisierten aktuellen Zustand zurueck
        return logger.execute(      # TODO Hier muss spaeter wieder das untere return unkommentiert werden
            lambda: ZustandsFactory(self.modell, self.uhr, self.info_manager).update_with_childs(result.zustand),
            f"\texecute_kommando -> update_with_childs( {result.zustand.__class__.__name__} )")
        # return ZustandsFactory(self.modell, self.uhr, self.info_manager).update_with_childs(result.zustand)

    # Funktion fuer den EventManager. Wird vom view usw. aufgerufen, wenn ein Kommando auf irgendeinen Weg an das
    #   System geschickt wird.
    def setze_cmd_str(self, cmd_str) -> None:
        self.cmd = cmd_str
        logger.start(f"setze_cmd_str mit {self.cmd[1:]} zustand = {self.aktueller_zustand.__class__.__name__}")
        self.aktueller_zustand = self.execute_kommando(self.cmd[1:])
        logger.fertig(f"setze_cmd_str -> execute_kommando(cmd) cmd = {self.cmd[1:]} zustand = {self.aktueller_zustand.__class__.__name__}")
        self.event_manager.publish_event(EventTyp.KOMMANDO_EXECUTED, self.aktueller_zustand)
        self.cmd = ''

    def programm_loop(self):
        self.modell.vokabelboxen.laden()
        logger.start()
        self.modell.vokabelkarten.laden()
        logger.fertig("programm_loop -> karten.laden()")
        # TODO Erstellen des InfoManagers blockiert das System, so dass der aktuelle zustand nicht gesetzt ist
        #   und Flaskview Fehlermeldungen (KeyError) beim Abrufen der Zeit ausgibt (siehe get_Routen in flaskview.py).
        logger.start()
        self.info_manager = InfoManager.factory(liste_der_boxen=self.modell.vokabelboxen.vokabelboxen,
                                                liste_der_karten=self.modell.vokabelkarten.vokabelkarten
                                                ).erzeuge_alle_infos(self.uhr.now(Lernuhr.echte_zeit()))
        logger.fertig("programm_loop -> InfoManager.factory(start)")

        print(f"Beginne mit der Arbeit. { self.info_manager.boxen_als_number_dict()[40] = }")
        logger.start()
        self.aktueller_zustand = (ZustandsFactory(self.modell, self.uhr, self.info_manager).
                                  buildZustandStart(ZustandsFactory.start_zustand()))
        logger.fertig("programm_loop -> buildZustandStart()")
        self.view_observer.views_updaten(self.aktueller_zustand, Lernuhr.echte_zeit())
        self.view_observer.views_rendern()

        while not isinstance(self.aktueller_zustand, ZustandsFactory.end_zustand()):
            self.aktueller_zustand = self.aktueller_zustand.update_zeit(self.uhr.as_iso_format(Lernuhr.echte_zeit()))
            self.event_manager.publish_event(EventTyp.LOOP_ENDE, self.aktueller_zustand)
            time.sleep(0.25)

        self.event_manager.publish_event(EventTyp.PROGRAMM_BENDET, self.aktueller_zustand)
