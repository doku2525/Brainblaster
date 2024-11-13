from __future__ import annotations
from abc import ABC
from typing import Type, Any
from random import randint
from dataclasses import dataclass, field
from src.classes import lernuhr
from src.classes.frageeinheit import Frageeinheit

import src.utils.utils_klassen as k_utils


@dataclass(frozen=True)
class Lerneinheit(ABC):
    eintrag: str = ""
    beschreibung: str = ""
    erzeugt: int = 0
    daten: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def fromdict(cls, source_dict: dict, klassenname: str = None) -> cls:
        """
        Dienst nur dazu, die entsprechende Unterklasse von Lerneinheit auszuwaehlen.
        :param source_dict:
        :param klassenname:
        :return:
        """
        lernklasse = k_utils.suche_subklasse_by_klassenname(Lerneinheit, klassenname)
        lernklasse = cls if lernklasse is None else lernklasse
        return lernklasse.fromdict(source_dict)

    def gleiche_lerneinheit_wie(self, lerneinheit: Lerneinheit) -> bool:
        return self.eintrag == lerneinheit.eintrag and self.beschreibung == lerneinheit.beschreibung

    def absolut_gleich_wie(self, lerneinheit: Lerneinheit) -> bool:
        return self.gleiche_lerneinheit_wie(lerneinheit) and self.erzeugt == lerneinheit.erzeugt

    # def to_lerneinheit(self) -> Lerneinheit:
    #     # TODO der Sinn dieser Methode ist mir noch komplett schleierhaft!
    #     return LerneinheitStandard(eintrag, beschreibung, erzeugt, daten)

    @classmethod
    def suche_meine_frageeinheiten(cls) -> list[Type[Frageeinheit]]:
        return Frageeinheit.suche_frageeinheiten_der_lernklasse(cls)


@dataclass(frozen=True)
class LerneinheitStandard(Lerneinheit):

    @classmethod
    def fromdict(cls, source_dict: dict, klassenname: str = None) -> cls:
        return cls(eintrag=source_dict['eintrag'],
                   beschreibung=source_dict['beschreibung'],
                   erzeugt=source_dict['erzeugt'],
                   daten=source_dict['daten'])


@dataclass(frozen=True)
class LerneinheitJapanisch(Lerneinheit):
    lesung: str = ""

    @classmethod
    def fromdict(cls, source_dict: dict, klassenname: str = None) -> cls:
        return cls(eintrag=source_dict['eintrag'],
                   beschreibung=source_dict['beschreibung'],
                   lesung=source_dict['lesung'],
                   erzeugt=source_dict['erzeugt'],
                   daten=source_dict['daten'])

    def gleiche_lerneinheit_wie(self, lerneinheit: Lerneinheit) -> bool:
        return super().gleiche_lerneinheit_wie(lerneinheit) and self.lesung == lerneinheit.lesung

    def absolut_gleich_wie(self, lerneinheit: Lerneinheit) -> bool:
        return self.gleiche_lerneinheit_wie(lerneinheit) and self.erzeugt == lerneinheit.erzeugt


@dataclass(frozen=True)
class LerneinheitJapanischKanji(Lerneinheit):
    on_lesung: str = ""
    kun_lesung: str = ""

    @classmethod
    def fromdict(cls, source_dict: dict, klassenname: str = None) -> cls:
        return cls(eintrag=source_dict['eintrag'],
                   beschreibung=source_dict['beschreibung'],
                   on_lesung=source_dict['on_lesung'],
                   kun_lesung=source_dict['kun_lesung'],
                   erzeugt=source_dict['erzeugt'],
                   daten=source_dict['daten'])

    def gleiche_lerneinheit_wie(self, lerneinheit: Lerneinheit) -> bool:
        return (super().gleiche_lerneinheit_wie(lerneinheit)
                and self.onLesung == lerneinheit.onLesung
                and self.kunLesung == lerneinheit.kunLesung)

    def absolut_gleich_wie(self, lerneinheit: Lerneinheit) -> bool:
        return self.gleiche_lerneinheit_wie(lerneinheit) and self.erzeugt == lerneinheit.erzeugt


@dataclass(frozen=True)
class LerneinheitChinesisch(Lerneinheit):
    traditionell: str = ""
    pinyin: str = ""
    zhuyin: str = ""

    @classmethod
    def fromdict(cls, source_dict: dict, klassenname: str = None) -> cls:
        return cls(eintrag=source_dict['eintrag'],
                   beschreibung=source_dict['beschreibung'],
                   traditionell=source_dict['traditionell'],
                   pinyin=source_dict['pinyin'],
                   zhuyin=source_dict['zhuyin'],
                   erzeugt=source_dict['erzeugt'],
                   daten=source_dict['daten'])

    def gleiche_lerneinheit_wie(self, lerneinheit: Lerneinheit) -> bool:
        return super().gleiche_lerneinheit_wie(lerneinheit) and self.pinyin == lerneinheit.pinyin

    def absolut_gleich_wie(self, lerneinheit: Lerneinheit) -> bool:
        return self.gleiche_lerneinheit_wie(lerneinheit) and self.erzeugt == lerneinheit.erzeugt


class LerneinheitFactory:

    @staticmethod
    def erzeuge_standard_beispiele(anzahl: int) -> list[Lerneinheit]:
        if anzahl == 0:
            return []
        else:
            return [LerneinheitStandard(eintrag="StandEint" + str(count),
                                        beschreibung="StandBesch" + str(count),
                                        erzeugt=lernuhr.Lernuhr(0, 0, 0, 0, lernuhr.UhrStatus.LAEUFT).echte_zeit()
                                                + (10000 * count) + randint(1, 100),
                                        daten={"daten": count}) for count in range(1, anzahl+1)]

    @staticmethod
    def erzeuge_japanisch_beispiele(anzahl: int) -> list[Lerneinheit]:
        if anzahl == 0:
            return []
        else:
            return [LerneinheitJapanisch(eintrag="日本語Eint" + str(count),
                                         beschreibung="日本語Besch" + str(count),
                                         lesung="日本語Lesu" + str(count),
                                         erzeugt=lernuhr.Lernuhr(0, 0, 0, 0, lernuhr.UhrStatus.LAEUFT).echte_zeit()
                                                 + (10000 * count) + randint(1, 100),
                                         daten={"daten": count}) for count in range(1, anzahl+1)]

    @staticmethod
    def erzeuge_japanisch_kanji_beispiele(anzahl: int) -> list[Lerneinheit]:
        if anzahl == 0:
            return []
        else:
            return [LerneinheitJapanischKanji(eintrag="漢字Eint" + str(count),
                                              beschreibung="漢字Besch" + str(count),
                                              on_lesung="漢字On" + str(count),
                                              kun_lesung="漢字Kun" + str(count),
                                              erzeugt=lernuhr.Lernuhr(0, 0, 0, 0, lernuhr.UhrStatus.LAEUFT).echte_zeit()
                                                      + (10000 * count) + randint(1, 100),
                                              daten={"daten": count}) for count in range(1, anzahl+1)]

    @staticmethod
    def erzeuge_chinesisch_beispiele(anzahl: int) -> list[Lerneinheit]:
        if anzahl == 0:
            return []
        else:
            return [LerneinheitChinesisch(eintrag="ChinEint" + str(count),
                                          beschreibung="ChinBesch" + str(count),
                                          traditionell="ChinTrad" + str(count),
                                          pinyin="ChinPiny" + str(count),
                                          zhuyin="ChinZhuy" + str(count),
                                          erzeugt=lernuhr.Lernuhr(0, 0, 0, 0, lernuhr.UhrStatus.LAEUFT).echte_zeit()
                                                  + (10000 * count) + randint(1, 100),
                                          daten={"daten": count}) for count in range(1, anzahl+1)]
