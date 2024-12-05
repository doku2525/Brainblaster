from __future__ import annotations
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from itertools import groupby
from typing import Iterable, NamedTuple, Type, TYPE_CHECKING

from src.classes.statistik import StatModus
from src.classes.statistikfilter import StatistikfilterPruefen, StatistikfilterNeue, StatistikfilterLernen

if TYPE_CHECKING:
    from src.classes.frageeinheit import Frageeinheit
    from src.classes.statistikfilter import SatistikfilterStrategie
    from src.classes.vokabelbox import Vokabelbox
    from src.classes.vokabelkarte import Vokabelkarte


InfotypStatModus = namedtuple('InfotypStatModus', ['insgesamt', 'aktuell'])


@dataclass(frozen=True)
class Lerninfos:
    box: Vokabelbox
    karten: Iterable[Vokabelkarte] = field(default_factory=Iterable)
    infos: dict = field(default_factory=dict)

    @property
    def gesamtzahl(self) -> int:
        return len(list(self.karten))

    def sammle_infos(self, uhrzeit: int) -> list[InfotypStatModus]:

        def build_entry(stat_filter: Type[SatistikfilterStrategie],
                        result: list[Vokabelkarte]) -> InfotypStatModus:
            return InfotypStatModus(insgesamt=result,
                                    aktuell=[karte for karte
                                             in result if stat_filter().filter(karte.lernstats,
                                                                               self.box.aktuelle_frage, uhrzeit)])

        tmp = Lerninfos.split_vokabelliste_by_status(list(self.karten), self.box.aktuelle_frage)
        return [
            build_entry(StatistikfilterPruefen, tmp[0]),
            build_entry(StatistikfilterLernen, tmp[1]),
            build_entry(StatistikfilterNeue, tmp[2]),
        ]

    @staticmethod
    def split_vokabelliste_by_status(vokabelliste: list[Vokabelkarte],
                                     aktuelle_frage: Type[Frageeinheit]
                                     ) -> tuple[list[Vokabelkarte], list[Vokabelkarte], list[Vokabelkarte]]:

        def get_karten_modus(karte: Vokabelkarte) -> StatModus:
            return karte.lernstats.statistiken[aktuelle_frage].modus

        grouped = groupby(vokabelliste, key=get_karten_modus)       # Gruppiere.
        result = defaultdict(list)                                  # Benutze defaultdict,
        for modus, group in grouped:                                # um alle Listen mit gleichem modus
            result[modus] += list(group)                            # zu einer Liste pro modus zusammenzufuehren.

        # Erzeuge result_tupel mit der entsprechenden Reihenfolge
        return result.get(StatModus.PRUEFEN, []), result.get(StatModus.LERNEN, []), result.get(StatModus.NEU, [])
