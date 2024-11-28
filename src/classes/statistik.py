from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from functools import reduce
import math
import src.utils.utils_enum as u_enum
from src.classes.antwort import Antwort


class StatModusStrategy(ABC):
    @abstractmethod
    def add_antwort(self, statistik: Statistik, antwort: Antwort) -> Statistik:
        """Fuege Antwort ans Ende der Statistik und setze den Modus und die Antwort anhaengig vom Modus"""
        pass

    @abstractmethod
    def srs_zeit_in_millis(self, statistik: Statistik) -> int:
        """Berechne die SRS-Zeit in Millisekunden bis zur naechsten Wiederholung abhaengig vom Modus"""
        pass


class StatModusNeu(StatModusStrategy):
    def add_antwort(self, statistik: Statistik, antwort: Antwort) -> Statistik:
        """ Da es sinnlos ist, noch nicht gelernte Vokabeln in den Pruefen-Kreislauf aufzunehmen,
        ist der Falsch-Zweig deaktiviert."""
        # if antwort.ist_falsch():
        #     return Statistik(StatModus.LERNEN, statistik.antworten + [antwort])
        # else:
        #     return Statistik(StatModus.PRUEFEN, statistik.antworten + [antwort])
        if antwort.ist_richtig():
            return Statistik(StatModus.PRUEFEN, statistik.antworten + [antwort])
        else:
            return statistik

    def srs_zeit_in_millis(self, statistik: Statistik) -> int:
        return 0


class StatModusPruefen(StatModusStrategy):
    def add_antwort(self, statistik: Statistik, antwort: Antwort) -> Statistik:
        if antwort.ist_falsch():
            return Statistik(StatModus.LERNEN, statistik.antworten + [antwort])
        else:
            return Statistik(StatModus.PRUEFEN, statistik.antworten + [antwort])

    def srs_zeit_in_millis(self, statistik: Statistik) -> int:
        def sekunden_pro_tag(sekunden: int) -> int:
            return int(sekunden * 24 * 60 * 60)

        richtige_antworten = len([a for a in statistik.antworten if a.ist_richtig()])
        falsche_antworten = len([a for a in statistik.antworten if a.ist_falsch()])
        differenz = richtige_antworten - falsche_antworten
        if differenz < 5:
            return sekunden_pro_tag(0.5 * pow(2, differenz * 1)) * 1000
        else:
            return int(differenz * 60 * 60 * 24 * StatistikCalculations.ef(statistik)) * 1000


class StatModusLernen(StatModusStrategy):
    def add_antwort(self, statistik: Statistik, antwort: Antwort) -> Statistik:
        if antwort.ist_richtig() and StatistikCalculations.berechne_lernindex(statistik) == 1:
            return Statistik(StatModus.PRUEFEN, statistik.antworten + [Antwort(7, antwort.erzeugt)])
        elif antwort.ist_richtig() and StatistikCalculations.berechne_lernindex(statistik) < 1:
            return Statistik(StatModus.LERNEN, statistik.antworten + [Antwort(7, antwort.erzeugt)])
        else:
            return Statistik(StatModus.LERNEN, statistik.antworten + [Antwort(0, antwort.erzeugt)])

    def srs_zeit_in_millis(self, statistik: Statistik) -> int:
        lernindex = StatistikCalculations.berechne_lernindex(statistik)
        return int(24 * math.pow(2, lernindex * 1) * 60 * 60) * 1000


class StatModus(Enum):
    NEU = 1
    LERNEN = 2
    PRUEFEN = 3

    def klasse(self):
        old_to_new_map = {
            StatModus.NEU: NeuerStatModus.NEU,
            StatModus.LERNEN: NeuerStatModus.LERNEN,
            StatModus.PRUEFEN: NeuerStatModus.PRUEFEN
        }
        return old_to_new_map[self].klasse()


class NeuerStatModus(Enum):
    # TODO Issue #4 Das Durcheinander von NeuerStatModus und StatModus beseitigen. Siehe speichern mit pickle
    NEU = (1, StatModusNeu)
    LERNEN = (2, StatModusLernen)
    PRUEFEN = (3, StatModusPruefen)

    def __init__(self, value, klasse):
        self._value_ = value
        self.klasse = klasse


class StatistikCalculations:
    @staticmethod
    def berechne_lernindex(statistik: Statistik) -> int:
        if statistik.modus == StatModus.LERNEN:
            position = [i for i, antwort in enumerate(statistik.antworten) if antwort.ist_falsch()]
            liste_antworten_nach_letztem_falsch = statistik.antworten[max(position):] if position else []
            return len(list(filter(lambda antwort: antwort.ist_richtig_gelernt(),
                                   liste_antworten_nach_letztem_falsch))) - \
                len(list(filter(lambda antwort: antwort.ist_falsch_gelernt(),
                                liste_antworten_nach_letztem_falsch)))
        else:
            return 1

    @staticmethod
    def ef(statistik: Statistik) -> float:
        def ef_formel(a: float, b: int) -> float: return a - 0.8 + (0.28 * b) - (0.02 * b * b)
        meine_antworten = [a for a in statistik.antworten if not a.ist_lernen()]
        return reduce(ef_formel, [a.antwort for a in meine_antworten], 2.5)

    @staticmethod
    def berechne_millisekunden(statistik: Statistik) -> int:
        return statistik.modus.klasse().srs_zeit_in_millis(statistik)

    # @staticmethod
    # def map_statmods(modus: StatModus) -> NeuerStatModus:
    #     OLD_TO_NEW_MAP = {
    #         StatModus.NEU: NeuerStatModus.NEU,
    #         StatModus.LERNEN: NeuerStatModus.LERNEN,
    #         StatModus.PRUEFEN: NeuerStatModus.PRUEFEN
    #     }
    #     return OLD_TO_NEW_MAP[modus]


@dataclass(frozen=True)
class Statistik:
    modus: StatModus = field(default=StatModus.NEU)
    antworten: list[Antwort] = field(default_factory=list)

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(modus=u_enum.name_zu_enum(source_dict['modus'], StatModus),
                   antworten=[Antwort.fromdict(elem) for elem in source_dict['antworten']])

    def add_neue_antwort(self, antwort: Antwort) -> Statistik:
        """Fuege eine neue Antwort ans Ende der Statistik"""
        return self.modus.klasse().add_antwort(self, antwort)

    def add_neue_antworten(self, antwortenliste: list[Antwort]) -> Statistik:
        """Fuege eine Liste neuer Antworten ans Ende der Statistik"""
        if not antwortenliste:
            return self
        else:
            return self.add_neue_antworten(antwortenliste[:-1]).add_neue_antwort(antwortenliste[-1])

    def add_neue_antworten_aus_int(self, liste_mit_zahlen: list[int]) -> Statistik:
        """Wandle eine Liste von Zahlen zwischen 1-6 in Antworten um
        und fuege sie als neue Antworten ans Ende der Statistik"""
        return self.add_neue_antworten(list(map(lambda elem: Antwort(elem, 0), liste_mit_zahlen)))

    def erstes_datum(self) -> int:
        """Liefer das Datum der ersten Antwort"""
        return self.antworten[0].erzeugt

    def letztes_datum(self) -> int:
        """Liefer das Datum der letzten Antwort"""
        return self.antworten[-1].erzeugt

    def naechstes_datum(self) -> int:
        """Liefer das Datum fuer die naechste Wiederholung"""
        return self.letztes_datum() + StatistikCalculations.berechne_millisekunden(self)

    def ist_abzufragen(self, modus: StatModus, vergleichszeit: int) -> bool:
        """Liefert True, wenn das Datum fuer die naechste Wiederholung vor der Vergleichszeit liegt.
        True beudeutet, dass abgefragt werden sollte!"""
        return self.modus == modus and self.naechstes_datum() < vergleichszeit
