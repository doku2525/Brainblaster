from __future__ import annotations
from dataclasses import dataclass, field
import random
from typing import Iterable, Type, TYPE_CHECKING

from src.classes.frageeinheit import Frageeinheit
from src.classes.lerneinheit import Lerneinheit
from src.classes import statistik, statistikfilter
import src.utils.utils_klassen as k_utils

if TYPE_CHECKING:
    from src.classes.vokabelkarte import Vokabelkarte

""" Das Attribut selektor enthaelt eine Liste mit Strings, die Tests enthalten, welche durch eval() ausgwertet werden.
siehe Funktion filter_vokabelkarten()
Zum Beispiel: ('satz', True) in a.lerneinheit.daten.items()"""
# TODO Issue #22 Ein Weg finden, keine Strings mit eval() verwenden zu muessen. Siehe Funktion filter_rekursiv()
# TODO Issue #22 Fuer die Liste von Strings mit Tests einen eigenen Datentyp erstellen
""" Arbeite mit dictionarys, um strings in funktioen umzuwandeln."""

@dataclass(frozen=True)
class Vokabelbox:
    titel: str = ""
    lernklasse: Type[Lerneinheit] = None
    selektor: list[str] = field(default_factory=list)
    aktuelle_frage: Type[Frageeinheit] = None

    def __post_init__(self):
        # TODO Mit solchen Tricks zu arbeiten ist vielleicht nicht die beste Idee und ein Zeichen dafuer,
        #   am Design etwas zu veraendern. Siehe auskommentierte Funktion aktuelle_frage()
        object.__setattr__(self,
                           'aktuelle_frage',
                           self.verfuegbare_frageeinheiten()[0] if not self.aktuelle_frage else self.aktuelle_frage)

    # @property
    # # Zum setzen einer neuen aktuellen_frage durch replace() kann ich nicht auf das Attribut aktuelle_frage zugreifen.
    # def aktuelle_frage(self) -> Type[Frageeinheit]:
    #     return self.verfuegbare_frageeinheiten()[0] if self._aktuelle_frage is None else self._aktuelle_frage

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(titel=source_dict['titel'],
                   lernklasse=k_utils.suche_subklasse_by_klassenname(Lerneinheit, source_dict['lernklasse']),
                   selektor=[element for element in source_dict['selektor']],
                   aktuelle_frage=k_utils.suche_subklasse_by_klassenname(Frageeinheit, source_dict['aktuelle_frage']))

    def __lt__(self, other):
        return self.titel < other.titel

    def rename(self, titel: str) -> Vokabelbox:
        return Vokabelbox(titel, self.lernklasse, self.selektor)

    def verfuegbare_frageeinheiten(self) -> list[Type[Frageeinheit]]:
        """
        Liefert die Klassen von Frageeinheit, die fuer die self.lernklasse verfuegbar sind
        :return: list[Type[Frageeinheit]]
        """
        return Frageeinheit.suche_frageeinheiten_der_lernklasse(self.lernklasse)

    def ist_erste_frageeinheit(self) -> bool:
        """
        Testet, ob die aktuelle Frage die erste in der Liste der verfuegbaren Fragen ist.
        :return: bool
        """
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        return current_index == 0

    def ist_letzte_frageeinheit(self) -> bool:
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        return current_index + 1 == len(self.verfuegbare_frageeinheiten())

    def naechste_frageeinheit(self) -> Vokabelbox:
        """ Wenn die aktuelle Frageeinheit die Letzte ist, dann liefert die naechste_frageeinheit() die Erste"""
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        if current_index + 1 == len(self.verfuegbare_frageeinheiten()):
            return Vokabelbox(self.titel, self.lernklasse, self.selektor, self.verfuegbare_frageeinheiten()[0])
        else:
            return Vokabelbox(self.titel, self.lernklasse,
                              self.selektor, self.verfuegbare_frageeinheiten()[current_index + 1])

    def vorherige_frageeinheit(self) -> Vokabelbox:
        """ Wenn die aktuelle Frageeinheit die Erste ist, dann liefert die vorherige_frageeinheit() die Letzte"""
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        return Vokabelbox(self.titel, self.lernklasse, self.selektor,
                          self.verfuegbare_frageeinheiten()[current_index - 1])

    def filter_vokabelkarten(self, kartenliste: list[Vokabelkarte]) -> Iterable[Vokabelkarte]:
        karten_der_lernklasse = [karte for karte in kartenliste if karte.lerneinheit.__class__ is self.lernklasse]

        def filter_rekursiv(result: Iterable[Vokabelkarte], filter_funcs: list[str]):
            """Die Filterfunktionen sind als String gespeichert, um sie mit einem Texteditor bearbeiten zu koennen"""
            if not filter_funcs:
                return result
            else:
                return filter_rekursiv(filter(lambda a: eval(filter_funcs[0]), result), filter_funcs[1:])
        return filter_rekursiv(karten_der_lernklasse, self.selektor)
