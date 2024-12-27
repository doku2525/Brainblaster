from __future__ import annotations
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field, replace
from itertools import groupby
import numpy as np
from typing import Iterable, NamedTuple, Type, TYPE_CHECKING

from src.classes.statistik import StatModus
from src.classes.statistikfilter import StatistikfilterPruefen, StatistikfilterNeue, StatistikfilterLernen

if TYPE_CHECKING:
    from src.classes.frageeinheit import Frageeinheit
    from src.classes.statistikfilter import SatistikfilterStrategie
    from src.classes.vokabelbox import Vokabelbox
    from src.classes.vokabelkarte import Vokabelkarte


#InfotypStatModus = namedtuple('InfotypStatModus', ['insgesamt', 'aktuell'])
"""Insgesamt ist die Anzahl aller Statistiken, die den entsprechenden Modus haben.
   Aktuell ist die Anzahl aller Statisitken, die im entsprechenden Test ausgewaehlt werden wuerden.
        Z.B. Insgaesamt 40 Karten mit dem Status PRUEFEN, aber nur 10 Karten davon sind pruefen() == True"""
class InfotypStatModus(NamedTuple):
    insgesamt: list[Vokabelkarte]
    aktuell: list[Vokabelkarte]

    def as_number_dict(self) -> dict:
        """Wandelt sich selbst und die InfotypStatModus-Objekte in den Values in ein Dictionary um"""
        return {str(key): len(value) for key, value in self._asdict().items()}


class InfotypStatistik(NamedTuple):
    pruefen: InfotypStatModus
    lernen: InfotypStatModus
    neu: InfotypStatModus

    def asdict(self) -> dict:
        """Wandelt sich selbst und die InfotypStatModus-Objekte in den Values in ein Dictionary um"""
        return {str(key): value._asdict() if hasattr(value, '_asdict') else value
                for key, value
                in self._asdict().items()}

    def as_number_dict(self) -> dict:
        """Wandelt sich selbst und die InfotypStatModus-Objekte in den Values in ein Dictionary um"""
        return {str(key): value.as_number_dict() for key, value in self._asdict().items()}


@dataclass(frozen=True)
class InfotypMatrix:
    matrix: np.ndarray = field(default_factory=np.ndarray)

    @classmethod
    def from_infotype_statistik_number_dict(cls, data_dic: dict) -> cls:
        return cls(np.array([[value['insgesamt'], value['aktuell']] for key, value in data_dic.items()]))

    def as_infotype_statistik_number_dict(self) -> dict:
        modi = ['pruefen', 'lernen', 'neu']
        return {modus: {'insgesamt': element[0], 'aktuell': element[1]}
                for modus, element
                in zip(modi, self.matrix)}


@dataclass(frozen=True)
class Lerninfos:
    """Speichert die Karten der Box in karten, so dass dann z.B. karte is in lern_info.karten ausgefuehrt werden kann.
    infos beinhaltet die Statistik.infos zu jeder Frageeinheit mit den drei Modi PRUEFEN, LERNEN und NEU. Jeder
    Modus ist dann nochmal in INSGESAMT und AKTUELL (siehe InfotypStatModus) unterteilt.
    infos.keys() => die Frageeinheiten()
    info[Frageinheit] => InfotypStatistik"""
    box: Vokabelbox
    karten: list[Vokabelkarte] = field(default_factory=Iterable)
    infos: dict[Type[Frageeinheit], InfotypStatistik] = field(default_factory=dict)

    @property
    def gesamtzahl(self) -> int:
        return len(self.karten)

    def erzeuge_infos(self, uhrzeit: int) -> Lerninfos:
        info_dict = {f_einheit: self.sammle_infos_zu_frageeinheit(uhrzeit, f_einheit)
                     for f_einheit
                     in self.box.verfuegbare_frageeinheiten()}
        return replace(self, infos=info_dict)

    def sammle_infos_zu_frageeinheit(self, uhrzeit: int, frageeinheit: Type[Frageeinheit]) -> InfotypStatistik:
        """Liefert ein Objekt vom Typ InfotypStatistik mit den Werten zu jedem StatusTyp (PRUEFEN, LERNEN, NEU)
        einer Statistik."""
        def build_entry(stat_filter: Type[SatistikfilterStrategie],
                        result: list[Vokabelkarte]) -> InfotypStatModus:
            # TODO die Funktion build_entry() auslagern, damit man auch Zwischenergebnisse erzeugen kann
            return InfotypStatModus(insgesamt=result,
                                    aktuell=[karte for karte
                                             in result if stat_filter().filter(karte.lernstats,
                                                                               frageeinheit, uhrzeit)])

        tmp = Lerninfos.split_vokabelliste_by_status(list(self.karten), frageeinheit)
        return InfotypStatistik(pruefen=build_entry(StatistikfilterPruefen, tmp[0]),
                                lernen=build_entry(StatistikfilterLernen, tmp[1]),
                                neu=build_entry(StatistikfilterNeue, tmp[2]))

    def sammle_infos(self, uhrzeit: int) -> InfotypStatistik:
        """Sammelt die Infos zur aktuellen Frageeinheit.
        Ist einfach nur ein Aufruf von sammle_infos_zu_frageeinheit mit der aktuellen Frageeinheit als Parameter"""
        return self.sammle_infos_zu_frageeinheit(uhrzeit, self.box.aktuelle_frage)

    @staticmethod
    def split_vokabelliste_by_status(vokabelliste: list[Vokabelkarte],
                                     aktuelle_frage: Type[Frageeinheit]
                                     ) -> tuple[list[Vokabelkarte], list[Vokabelkarte], list[Vokabelkarte]]:
        """Gruppiert die VOKABELLISTE nach dem Modus der aktuellen Statistik mit dem dem Befehl itertools.groupby()
        und sammelt das Ergbnis in einem defaultdict mit dem Status als Schluessel und der Liste[Karten] als Wert"""
        def get_karten_modus(karte: Vokabelkarte) -> StatModus:
            return karte.lernstats.statistiken[aktuelle_frage].modus

        grouped = groupby(vokabelliste, key=get_karten_modus)       # Gruppiere.
        result = defaultdict(list)                                  # Benutze defaultdict,
        for modus, group in grouped:                                # um alle Listen mit gleichem modus
            result[modus] += list(group)                            # zu einer Liste pro modus zusammenzufuehren.

        # Erzeuge result_tupel mit der entsprechenden Reihenfolge
        return result.get(StatModus.PRUEFEN, []), result.get(StatModus.LERNEN, []), result.get(StatModus.NEU, [])
