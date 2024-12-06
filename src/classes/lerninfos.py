from __future__ import annotations
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field, replace
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
    karten: list[Vokabelkarte] = field(default_factory=Iterable)
    infos: dict = field(default_factory=dict)

    @property
    def gesamtzahl(self) -> int:
        return len(self.karten)

    def erzeuge_info_dict(self, uhrzeit: int) -> Lerninfos:
        info_dict = {f_einheit: self.sammle_infos_zu_frageeinheit(uhrzeit, f_einheit)
                     for f_einheit
                     in self.box.verfuegbare_frageeinheiten()}
        return replace(self, infos=info_dict)

    def sammle_infos_zu_frageeinheit(self, uhrzeit: int, frageeinheit: Type[Frageeinheit]) -> list[InfotypStatModus]:

        def build_entry(stat_filter: Type[SatistikfilterStrategie],
                        result: list[Vokabelkarte]) -> InfotypStatModus:
            return InfotypStatModus(insgesamt=result,
                                    aktuell=[karte for karte
                                             in result if stat_filter().filter(karte.lernstats,
                                                                               frageeinheit, uhrzeit)])

        tmp = Lerninfos.split_vokabelliste_by_status(list(self.karten), frageeinheit)
        return [
            build_entry(StatistikfilterPruefen, tmp[0]),
            build_entry(StatistikfilterLernen, tmp[1]),
            build_entry(StatistikfilterNeue, tmp[2]),
        ]

    def sammle_infos(self, uhrzeit: int) -> list[InfotypStatModus]:
        return self.sammle_infos_zu_frageeinheit(uhrzeit, self.box.aktuelle_frage)

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
