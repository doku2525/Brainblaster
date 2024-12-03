from __future__ import annotations
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field
from functools import reduce
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from src.classes.statistikfilter import SatistikfilterStrategie
    from src.classes.vokabelbox import Vokabelbox
    from src.classes.vokabelkarte import Vokabelkarte


KartenfilterTupel = namedtuple('KartenfilterTupel',
                               ['funktion', 'args', 'arg_name_liste'],
                               defaults=[lambda:None, {}, 'karten_liste'])


class KartenfilterStrategie(ABC):

    @abstractmethod
    def filter(self, karten_liste: list[Vokabelkarte]) -> list[Vokabelkarte]:
        pass

    @staticmethod
    def filter_karten(filter_tupel: list[KartenfilterTupel] = None,
                      liste: list[Vokabelkarte] = None) -> list[Vokabelkarte]:
        """ arg_name = der Argumentname, mit dem die Liste in der Filterfunktion uebergeben wird. Standard = 'liste'.
            WICHTIG!!! Bei Kartenfilter-Objekten die filter()-Funktion uebergeben nicht nur die Klasse.
            So => filter_karten( [KlasseA(...).filter, KlasseB(...).filter] , [vokabelkarten]) """
        match (filter_tupel is None or filter_tupel == [], liste is None or liste == []):
            case (_, True):         # Reihenfolge wichtig! Zuerst liste == None abfangen, damit Ergebnis nicht None ist.
                return []
            case (True, _):
                return liste
            case _:
                try:  # Pruefe, ob Argument arg_name exisitiert mit dem ersten Element aus den Listen
                    filter_tupel[0].funktion(**filter_tupel[0].args | {filter_tupel[0].arg_name_liste: liste[:1]})
                except TypeError:
                    return []
                else:
                    return reduce(lambda v_liste, f_tupel: f_tupel.funktion(**(f_tupel.args |
                                                                               {f_tupel.arg_name_liste: v_liste})),
                                  filter_tupel,
                                  liste)


@dataclass(frozen=True)
class FilterKartenstatistik:
    strategie: Type[SatistikfilterStrategie]
    vokabelbox: Vokabelbox
    zeit: int

    def filter(self, karten_liste: list[Vokabelkarte]) -> list[Vokabelkarte]:
        return [karte
                for karte
                in karten_liste if self.strategie().filter(stat_manager=karte.lernstats,
                                                           frage=self.vokabelbox.aktuelle_frage,
                                                           vergleichszeit=self.zeit)]


@dataclass(frozen=True)
class FilterVokabelbox:
    vokabelbox: Vokabelbox

    def filter(self, karten_liste: list[Vokabelkarte]) -> list[Vokabelkarte]:
        return self.vokabelbox.filter_vokabelkarten(karten_liste)
