from abc import ABC, abstractmethod
from src.classes.statistikmanager import StatistikManager
from src.classes.frageeinheit import Frageeinheit
from src.classes.statistik import StatModus, StatistikCalculations
from typing import Type


class AbfragefilterStrategie(ABC):
    # TODO TEST gesamte Klasse
    @abstractmethod
    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        pass


class PruefenFilter(AbfragefilterStrategie):

    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        return (stat_manager.statistiken[frage].modus == StatModus.PRUEFEN
                and stat_manager.statistiken[frage].ist_abzufragen(StatModus.PRUEFEN, vergleichszeit))


class NeueFilter(AbfragefilterStrategie):

    def filter(self, stat_manager: StatistikManager, frageklasse: Type[Frageeinheit], vergleichszeit: int) -> bool:
        aktuelle_statistik = stat_manager.statistiken[frageklasse]
        zeitdauer = 14 * 86400000  # 1 Tag = 86400000 ms
        vorherige_statistik = stat_manager.statistiken[Frageeinheit.vorherige_frageeinheit(frageklasse)] if not Frageeinheit.ist_erste_frageeinheit(frageklasse) else None
        if vorherige_statistik:
            return (aktuelle_statistik.modus == StatModus.NEU
                    and StatistikCalculations.berechne_millisekunden(vorherige_statistik) > zeitdauer
                    and vorherige_statistik.letztes_datum() < vergleichszeit
                    and vorherige_statistik.modus == StatModus.PRUEFEN)
        else:
            return aktuelle_statistik.modus == StatModus.NEU


class LernenFilter(AbfragefilterStrategie):

    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        return (stat_manager.statistiken[frage].modus == StatModus.LERNEN
                and stat_manager.statistiken[frage].ist_abzufragen(StatModus.LERNEN, vergleichszeit))


class LernenAlleFilter(AbfragefilterStrategie):

    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        return stat_manager.statistiken[frage].modus == StatModus.LERNEN
