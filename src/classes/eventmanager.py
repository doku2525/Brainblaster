from __future__ import annotations
from enum import Enum
from typing import Any, Callable


class EventTyp(Enum):
    NEU_DATEN = 0
    UPDATE_VIEW = 1
    RENDER_VIEW = 2
    NEUES_KOMMANDO = 3
    KOMMANDO_EXECUTED = 4
    LOOP_ENDE = 5
    PROGRAMM_BENDET = 6


class EventManager:
    def __init__(self):
        self.events: dict = {}

    def subscribe(self, event_type: EventTyp, funktion: Callable) -> EventManager:
        if event_type not in self.events:
            self.events[event_type] = []
        self.events[event_type].append(funktion)
        return self

    def unsubscribe(self, event_type: EventTyp, funktion: Callable) -> EventManager:
        if event_type in self.events:
            self.events[event_type] = [func for func in self.events[event_type] if func != funktion]
        self.events = {key: value for key, value in self.events.items() if value}
        return self

    def publish_event(self, event_type: EventTyp, data: Any) -> EventManager:
        if event_type in self.events:
            for func in self.events[event_type]:
                func(data)
        return self
