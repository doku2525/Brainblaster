from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
import time

from src.classes.eventmanager import EventTyp
from src.classes.infomanager import InfoManager
from src.classes.taskmanager import Task
from src.zustaende.zustandsfactory import ZustandsFactory

if TYPE_CHECKING:
    from src.classes.eventmanager import EventManager
    from src.classes.vokabeltrainercontroller import VokabeltrainerController
    from src.kommandos.kommandointerpreter import KommandoInterpreter
    from src.zustaende.workflowmanager import WorkflowManager

"""
Die Klasse fuehrt die programm_schleife aus und verarbeitet die von den Views usw. gesendeten Kommandos.
Die beiden wesentlichen Funktionen sind:
kommando_event_handler()
start()
"""
@dataclass
class ProgrammLoop:
    controller: VokabeltrainerController
    workflow: WorkflowManager
    cmd_interpreter: KommandoInterpreter
    event_manager: EventManager
    cmd: str = field(default='')

    def __post_init__(self):
        print(f"ProgrammLoop: {self.workflow.aktueller_zustand.__name__ = }")
        self.lade_repositories()
        self.register_cmds_in_event_manager()
        self.erzeuge_task_info_manager()
        # Zum Erzeugen des StartZustands muss der InfoManagerTask erst beendet sein. (siehe Bemerkung in Funktion)
        # starte_workflow_task()
        self.controller.aktueller_zustand = (
            ZustandsFactory(self.controller.modell, self.controller.uhr, self.controller.info_manager).
            buildZustandStart(ZustandsFactory.start_zustand()))
        self.controller.view_observer.views_updaten(self.controller.aktueller_zustand, self.controller.uhr.echte_zeit())
        self.controller.view_observer.views_rendern()

    def register_cmds_in_event_manager(self) -> EventManager:
        self.event_manager.subscribe(EventTyp.NEUES_KOMMANDO, self.kommando_event_handler)
        self.event_manager.subscribe(
            EventTyp.KOMMANDO_EXECUTED,
            lambda zustand: self.controller.view_observer.views_updaten(zustand, self.controller.uhr.echte_zeit()))
        self.event_manager.subscribe(
            EventTyp.LOOP_ENDE,
            lambda zustand: self.controller.view_observer.views_updaten(zustand, self.controller.uhr.echte_zeit()))
        self.event_manager.subscribe(
            EventTyp.KOMMANDO_EXECUTED,
            lambda zustand: self.controller.view_observer.views_rendern())
        self.event_manager.subscribe(
            EventTyp.PROGRAMM_BENDET,
            lambda zustand: self.view_observer.views_rendern())
        return self.event_manager

    def lade_repositories(self) -> VokabeltrainerController:
        self.controller.modell.vokabelboxen.laden()
        self.controller.modell.vokabelkarten.laden()
        return self.controller

    def erzeuge_task_info_manager(self) -> VokabeltrainerController:
        self.controller.starte_info_und_task_manager()
        return self.controller

    def execute_controller_kommando(self, cmd: list[str]) -> VokabeltrainerController:
        """Analysiet Kommando und leitet Kommando an entsprechende Klassen weiter."""
        kommando, args = self.controller.aktueller_zustand.parse_user_eingabe(cmd)
        self.controller = self.cmd_interpreter.execute(kommando, self.controller, args)
        return self.controller

    def execute_workflow_kommando(self, cmd: list[str]) -> WorkflowManager:
        match (list(cmd)):
            case ['@', *zustands_name]: return self.workflow.transition_zu_per_namen(''.join(zustands_name))
            case ['0']: return self.workflow.go_back()
            case [*index] if ''.join(index).isdigit():
                return self.workflow.transition_zu_per_index(int(''.join(index)) - 1)
            case _: return self.worklflow

    def aktuallisiere_zustand_in_controller(self) -> VokabeltrainerController:
        """ Hier sollte das Commando an den WorklfowManager uebergeben werden
            moegliche Kommandos:
            - @ + KlassenName des Zustands als String
            - 0 zurueck zur Elternklasse
            - 1..n Klasse an der n-ten Position in der child-Liste/transitions-Liste
            - '' Leerer String fuer keine Veraenderung"""
        """ Da Lernuhr keine Child hat, wird die Aufrufende sowohl in Parrent als auch in Child gespeichert.
        Bisher ist es so, dass bei 0 nur der Parrentzustand als erstes Element im ZustandReturnValue
        uebergeben werden. cmd und args sind Leer.
        Ansonsten wird die in Child gespeicherte aufrufende Klasse zusammen
        mit **{'cmd': 'update_uhr', 'args': (self.neue_uhr,)} aufgerufen. self.neue_uhr ist vom Typ Lernuhr."""
        if self.controller.aktueller_zustand.__class__ != self.workflow.aktueller_zustand:
            self.controller.aktueller_zustand = (
                ZustandsFactory(self.controller.modell, self.controller.uhr, self.controller.info_manager).
                build(self.workflow.aktueller_zustand))
        return self.controller

    def kommando_event_handler(self, cmd_str) -> None:
        """Verarbeitet die vom Event-Manager(z.B. durch die Views) mit NEUES_KOMMANDO gesendeten Kommandostrings.
        Kommandos fuer
            den KommandoInterpreter beginnen mit 'c' wie in 'command'
            den WorkflowManager beginnen mit 'z' wie in 'zustand'
        """
        self.cmd = cmd_str  # FLAG setzen
        # Kommando den verschiedenen Klassen uebergeben
        match (list(cmd_str)):
            case ['c', *cmd]: self.controller = self.execute_controller_kommando(cmd
                                                                                 )
            case ['z', *cmd]: self.workflow = self.execute_workflow_kommando(cmd)

        self.controller = self.aktuallisiere_zustand_in_controller()

        # Sende Event an alle Abonnenten von KOMMANDO_EXECUTED, die auf den aktuallisierten Zustand warten
        self.event_manager.publish_event(EventTyp.KOMMANDO_EXECUTED, self.controller.aktueller_zustand)
        self.cmd = ''   # FLAG loeschen

    def start(self):
        while not isinstance(self.controller.aktueller_zustand, ZustandsFactory.end_zustand()):
            self.controller.aktueller_zustand = self.controller.aktueller_zustand.update_zeit(
                self.controller.uhr.as_iso_format(self.controller.uhr.echte_zeit()))
            self.event_manager.publish_event(EventTyp.LOOP_ENDE, self.controller.aktueller_zustand)
            time.sleep(0.25)

        self.event_manager.publish_event(EventTyp.PROGRAMM_BENDET, self.controller.aktueller_zustand)
