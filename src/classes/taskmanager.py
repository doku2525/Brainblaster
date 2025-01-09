from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import threading
from concurrent.futures import ThreadPoolExecutor, Future


class TaskLeerlaufzeit(Enum):
    NULL = 0
    NIEDRIG = 0.2
    MITTEL = 0.5
    HOCH = 1


@dataclass
class Task:
    """Fuehrt sequentielle Veraendrungen auf den/das in value gespeicherte/n Wert/Objekt aus."""
    value: Any
    executor: ThreadPoolExecutor = ThreadPoolExecutor()
    auftraege: list = field(default_factory=list)
    future: Future = None
    arbeits_thread: threading.Thread = None
    __thread_beenden: bool = False                           # Flag zum beenden des arbeits_threads
    leerlaufzeit: TaskLeerlaufzeit = TaskLeerlaufzeit.NULL   # Wartezeit in sek im Thread, um CPU-Last zu verringern

    def registriere_funktion(self, funktion: Callable) -> None:
        self.auftraege.append(funktion)

    def start(self):

        def worker():
            while not self.__thread_beenden:
                while self.auftraege:
                    task = self.auftraege.pop()
                    self.future = self.executor.submit(task, self.value)
                    self.value = self.future.result()
                if self.leerlaufzeit.value > 0:
                    time.sleep(self.leerlaufzeit.value)

            self.__thread_beenden = False

        # Starte einen neuen Thread für die Aufgabenabarbeitung
        self.arbeits_thread = threading.Thread(target=worker)
        self.arbeits_thread.start()

    def stop(self):
        self.__thread_beenden = True

    def is_running(self) -> bool:
        return ((self.future is not None) and (not self.future.done())) or self.auftraege != []

    def is_alive(self) -> bool:
        return self.arbeits_thread.is_alive() if self.arbeits_thread else False

    def join(self, leerlauf: float = 0.1) -> None:
        """Warte, bis alle Auftraege abgearbeitet sind."""
        while self.is_running():
            time.sleep(leerlauf)


@dataclass
class TaskManager:
    tasks: dict = field(default_factory=dict)

    def registriere_task(self, name: str, task: Task) -> None | Task:
        """Falls ein Task mit dem gleichen Namen existiert, dann wird er im Taskmanager durch den neuen Task ersetzt.
            Der alte Task wird aber als Ergebnis zurueckgeliefert."""
        alter_task = self.tasks.get(name, None)
        self.tasks[name] = task
        return alter_task

    def task(self, name: str) -> Task:
        return self.tasks[name]
