"""
Hilfsfunktionen in Bezug auf Enum-Funktionen
"""
from enum import Enum
from typing import TypeVar, Generic, Type


T = TypeVar('T', bound=Enum)


def name_zu_enum(name: str, enum_klasse: Type[T]) -> T:
    return enum_klasse[name]


def enum_zu_dict(objekt: Enum) -> str:
    return objekt.name
