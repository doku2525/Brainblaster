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
from src.classes.taskmanager import TaskManager, Task
from src.zustaende.zustandsfactory import ZustandsFactory
import src.utils.utils_io as u_io
import src.utils.utils_performancelogger as u_log

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.classes.zustandsbeobachter import ObserverManager
    from src.classes.vokabelkarte import Vokabelkarte
    from src.zustaende.zustand import Zustand


# Initializiere Logger
logger = u_log.ZeitLogger.create(f"{config.log_pfad}performance.log", __name__)
logger.starte_logging()


class VokabeltrainerController:

    def __init__(self,
                 modell: VokabeltrainerModell,
                 uhr: Lernuhr,
                 view_observer: ObserverManager,
                 task_manager: TaskManager = None):

        self.modell: VokabeltrainerModell = modell
        self.info_manager: InfoManager = InfoManager()
        self.uhr: Lernuhr = uhr
        self.aktueller_zustand: Zustand | None = None
        self.view_observer: ObserverManager = view_observer
#        self.cmd: str = ''
        self.task_manager = task_manager

    # ###########################################################################################
    #   TaskManager-Funktionen - Funktionen, die nur fuer den TaskManager geeignet sind
    # ###########################################################################################
    """ Variablen, die vom Taskmanager verwaltet werden sollen, duerfen dann nur noch ueber die Funktionen in den
        Tasks veraendert werden. Die result Funktionen, die vom Wrapper an den Task uebergeben werden muss folgende
        Form haben:
        wrapper_func(paramaterliste) -> Callable:
         def result_func(obj: T) -> T:
            self.variable = obj.func()
            return self.variable
         return result_func"""

    def __task_funktion_erzeuge_infos(self, zeit: int) -> Callable:
        """Hilfsfunktion in programm_loop() und update_uhr() fuer den Taskmanager zum erzeugen der Infos und
            Aktuallisieren von self.info_manager"""
        def result_func(obj: InfoManager) -> InfoManager:
            logger.start(" TASKFUNKTION erzeuge_alle_infos")
            self.info_manager = obj.erzeuge_alle_infos(zeit)
            logger.fertig(" TASKFUNKTION erzeuge_alle_infos")
            return self.info_manager
        return result_func

    def __task_funktion_update_infos(self, karte_alt: Vokabelkarte, karte_neu: Vokabelkarte, zeit: int) -> Callable:
        """Hilfsfunktion in update_vokabelkarte_statistik() fuer den Taskmanager zum berechnen der Infos und
            Aktuallisieren von self.info_manager"""
        def result_func(obj: InfoManager) -> InfoManager:
            logger.start(" TASKFUNKTION update_infos_fuer_karte")
            self.info_manager = obj.update_infos_fuer_karte(karte_alt, karte_neu, zeit)
            logger.fertig(" TASKFUNKTION update_infos_fuer_karte")
            return self.info_manager
        return result_func

    # ###########################################################################################
    #   Systemkommandos, die vom KommandoInterpreter aufgerufen werden.
    # ###########################################################################################
    def update_uhr(self, neue_uhr: Lernuhr) -> None:
        self.uhr = neue_uhr
        logger.start()
        # Registriere die Funktion mit den aktuellen Werten als Parameter im Taskmanager
        #   Der Taskmanager fuer 'INFO_MANAGER' wurde schon in programm_loop() gestartet
        if self.task_manager:
            self.task_manager.task('INFO_MANAGER').registriere_funktion(
                self.__task_funktion_erzeuge_infos(self.uhr.now(Lernuhr.echte_zeit())))
        else:
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
        logger.start(f"\tupdate_vokabelkarte_statistik  task_funktion_update_infos an Taskmanager geschickt")

        # Registriere die Funktion mit den aktuellen Werten als Parameter im Taskmanager, falls Taskmanager existiert
        #   Der Taskmanager fuer 'INFO_MANAGER' wurde schon in programm_loop() gestartet
        if self.task_manager:
            self.task_manager.task('INFO_MANAGER').registriere_funktion(
                self.__task_funktion_update_infos(alte_karte, neue_karte, self.uhr.now(Lernuhr.echte_zeit())))
        else:
            self.info_manager = self.info_manager.update_infos_fuer_karte(alte_karte,
                                                                          neue_karte,
                                                                          self.uhr.now(Lernuhr.echte_zeit()))
        logger.fertig(f"\tupdate_vokabelkarte_statistik  task_funktion_update_infos an Taskmanager geschickt")

    def speicher_daten_in_dateien(self):
        print(f"Beginne mit speichern")

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

    def starte_info_und_task_manager(self):
        self.info_manager = InfoManager.factory(liste_der_boxen=self.modell.vokabelboxen.vokabelboxen,
                                                liste_der_karten=self.modell.vokabelkarten.vokabelkarten
                                                )

        # Registriere InfoManager im Taskmanager
        if self.task_manager:
            self.task_manager.registriere_task('INFO_MANAGER', Task(self.info_manager))
            self.task_manager.task('INFO_MANAGER').start()

        if self.task_manager:
            self.task_manager.task('INFO_MANAGER').registriere_funktion(
                self.__task_funktion_erzeuge_infos(self.uhr.now(Lernuhr.echte_zeit())))
            # Task muss beendet sein fuer folgenden Block. Siehe Kommentar im folgenden Block mit self.aktueller_zustand
            self.task_manager.task('INFO_MANAGER').join()
        else:
            self.info_manager = self.info_manager.erzeuge_alle_infos(self.uhr.now(Lernuhr.echte_zeit()))
