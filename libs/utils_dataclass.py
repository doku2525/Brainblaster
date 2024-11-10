"""
Hilfsfunktionen fuer Operationen auf Dataclasses
"""
from typing import Any
from enum import Enum
from dataclasses import asdict
import importlib


def asdict_factory(items):
    # TODO Test
    return {key: (
        value.name if isinstance(value, Enum) else      # Lege Value fuer Enumtyp fest
        value.__name__ if isinstance(value, type) else  # Lege Value fuer dictionary fest
        value)                                          # Fuer alle anderen Elemente
        for key, value in (
            # Erzeuge das Tuple fuer Stastikmanager, wenn der Schluessel vom Typ type ist
            (item[0],                                                   # Der 1. Wert im Tupel bleibt unveraendert
             {key.__name__ if isinstance(key, type) else key: value     # Der 2. Wert im Tupel Wenn typ Type -> der Klassenname als String
              for key, value in item[1].items()})                       # Tupel fertig gebaut
            if isinstance(item[1], dict) else item                      # Baue das Tupel nur, wenn der der zweite Wert im item ein dict ist
            for item in items
        )
    }


def mein_asdict(daten_klasse: Any) -> dict:
    # TODO Test
    if isinstance(daten_klasse, importlib.import_module('vokabelkarte').Vokabelkarte):
        return ({'lernklasse': daten_klasse.lerneinheit.__class__.__name__} |
                asdict(daten_klasse, dict_factory=asdict_factory))
    return asdict(daten_klasse, dict_factory=asdict_factory)
