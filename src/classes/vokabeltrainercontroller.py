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
                 event_manager: EventManager, task_manager: TaskManager = None):
        self.modell: VokabeltrainerModell = modell
        self.info_manager: InfoManager = InfoManager()
        self.uhr: Lernuhr = uhr
        self.aktueller_zustand: Zustand | None = None
        self.view_observer: ObserverManager = view_observer
        self.event_manager: EventManager = event_manager
        self.cmd: str = ''
        self.task_manager = task_manager
        """ Variablen, die vom Taskmanager verwaltet werden sollen, duerfen dann nur noch ueber die Funktionen in den
            Tasks veraendert werden. Die result Funktionen, die vom Wrapper an den Task uebergeben werden muss folgende
            Form haben:
            wrapper_func(paramaterliste) -> Callable:
             def result_func(obj: T) -> T:
                self.variable = obj.func()
                return self.variable
             return result_func"""

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

    def __task_funktion_erzeuge_infos(self, zeit: int) -> Callable:
        """Hilfsfunktion in programm_loop() und update_uhr() fuer den Taskmanager zum erzeugen der Infos und
            Aktuallisieren von self.info_manager"""
        def result_func(obj: InfoManager) -> InfoManager:
            logger.start(" TASKFUNKTION erzeuge_alle_infos")
            self.info_manager = obj.erzeuge_alle_infos(zeit)
            logger.fertig(" TASKFUNKTION erzeuge_alle_infos")
            return self.info_manager

        return result_func

    # Definiere Systemkommandos, die von den Zustaenden aufgerufen werden koennen.
    #  Jede Funktion muss im command-Dictionary der Funktion execute_kommando() registriert werden
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

    def __task_funktion_update_infos(self, karte_alt: Vokabelkarte, karte_neu: Vokabelkarte, zeit: int) -> Callable:
        """Hilfsfunktion in update_vokabelkarte_statistik() fuer den Taskmanager zum berechnen der Infos und
            Aktuallisieren von self.info_manager"""
        def result_func(obj: InfoManager) -> InfoManager:
            logger.start(" TASKFUNKTION update_infos_fuer_karte")
            self.info_manager = obj.update_infos_fuer_karte(karte_alt, karte_neu, zeit)
            logger.fertig(" TASKFUNKTION update_infos_fuer_karte")
            return self.info_manager

        return result_func

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
        logger.fertig(f"setze_cmd_str -> execute_kommando(cmd) cmd = {self.cmd[1:]} " +
                      f"zustand = {self.aktueller_zustand.__class__.__name__}")
        self.event_manager.publish_event(EventTyp.KOMMANDO_EXECUTED, self.aktueller_zustand)
        self.cmd = ''

    def programm_loop(self):
        self.modell.vokabelboxen.laden()
        logger.start()
        self.modell.vokabelkarten.laden()
        logger.fertig("programm_loop -> karten.laden()")

        logger.start()
        # DAUER: 4.74630.
        self.info_manager = InfoManager.factory(liste_der_boxen=self.modell.vokabelboxen.vokabelboxen,
                                                liste_der_karten=self.modell.vokabelkarten.vokabelkarten
                                                )
        logger.fertig("programm_loop -> InfoManager.factory(start)")

        # Registriere InfoManager im Taskmanager
        if self.task_manager:
            self.task_manager.registriere_task('INFO_MANAGER', Task(self.info_manager))
            self.task_manager.task('INFO_MANAGER').start()

        logger.start()
        # DAUER: 3.10568
        if self.task_manager:
            self.task_manager.task('INFO_MANAGER').registriere_funktion(
                self.__task_funktion_erzeuge_infos(self.uhr.now(Lernuhr.echte_zeit())))
            # Task muss beendet sein fuer folgenden Block. Siehe Kommentar im folgenden Block mit self.aktueller_zustand
            self.task_manager.task('INFO_MANAGER').join()
        else:
            self.info_manager = self.info_manager.erzeuge_alle_infos(self.uhr.now(Lernuhr.echte_zeit()))

        logger.fertig("programm_loop -> info_manager.erzeuge_alle_infos()")

        print(f"Beginne mit der Arbeit. { self.info_manager.boxen_als_number_dict()[40] = }")
        logger.start()
        # TODO ZustandsFactory.buildStart Benoetigt zum erstellen des Child BoxInfo bereits einen InfoManager mit Daten
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
