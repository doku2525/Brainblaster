from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type
from src.classes.frageeinheit import Frageeinheit
from src.classes.lerneinheit import Lerneinheit
from src.classes.statistik import Statistik, StatModus

import src.utils.utils_klassen as k_utils


@dataclass(frozen=True)
class StatistikManager:
    statistiken: dict[Type[Frageeinheit], Statistik] = field(default_factory=dict)

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(statistiken={k_utils.suche_subklasse_by_klassenname(Frageeinheit, key): Statistik.fromdict(value)
                                for key, value
                                in source_dict['statistiken'].items()}) if source_dict is not None else None

    def liste_der_frageeinheiten(self) -> list[Type[Frageeinheit]]:
        """Sortiert nach rank (siehe Attribute Frageeinheit)"""
        liste_der_frageklassen = sorted([frage_klasse() for frage_klasse in self.statistiken.keys()])
        return [frage_instanze.__class__ for frage_instanze in liste_der_frageklassen]

    def titel_der_frageeinheiten(self) -> list[str]:
        return [frage_klasse().titel() for frage_klasse in self.liste_der_frageeinheiten()]

    def suche_frageeinheit_nach_titel(self, suchstring: str) -> Type[Frageeinheit]:
        return [frage_klasse for frage_klasse in self.statistiken.keys() if frage_klasse().titel() == suchstring][0]

    # TODO Issue #6 Noch viele auskommentierte Funktionen
    # def ist_erste_frageeinheit(self, frage_klasse: Type[Frageeinheit]) -> bool:
    #     return self.liste_der_frageeinheiten()[0] == frage_klasse

    # def ist_letzte_frageeinheit(self, frage_klasse: Type[Frageeinheit]) -> bool:
    #     return self.liste_der_frageeinheiten()[-1] == frage_klasse

    # def vorherige_frageeinheit(self, frage_klasse: Type[Frageeinheit]) -> Type[Frageeinheit]:
    #     """ Wenn frageeinheit die Erste ist, dann liefert vorherige_frageeinheit() die Letzte"""
    #     current_index = [index
    #                      for index, frage_klasse_tmp
    #                      in enumerate(self.liste_der_frageeinheiten())
    #                      if frage_klasse_tmp == frage_klasse][0]
    #     return self.liste_der_frageeinheiten()[current_index - 1]

    # def folgende_frageeinheit(self, frage_klasse: Type[Frageeinheit]) -> Type[Frageeinheit]:
    #     """ Wenn frageeinheit die Letzte ist, dann liefert folgende_frageeinheit() die Erste"""
    #     current_index = [index
    #                      for index, frage_klasse_tmp
    #                      in enumerate(self.liste_der_frageeinheiten())
    #                      if frage_klasse_tmp == frage_klasse][0]
    #     if current_index + 1 == len(self.liste_der_frageeinheiten()):
    #         return self.liste_der_frageeinheiten()[0]
    #     else:
    #         return self.liste_der_frageeinheiten()[current_index + 1]

    @staticmethod
    def erzeuge(lernklasse: Type[Lerneinheit]) -> StatistikManager:
        return StatistikManager({frage: Statistik(StatModus.NEU, []) for frage in
                                 Frageeinheit.suche_frageeinheiten_der_lernklasse(lernklasse)})
