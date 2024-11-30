from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type, TYPE_CHECKING
from src.classes.frageeinheit import Frageeinheit
from src.classes.statistik import StatModus, StatistikCalculations
if TYPE_CHECKING:
    from src.classes.statistikmanager import StatistikManager


class SatistikfilterStrategie(ABC):
    """AbfrageFilter beziehen sich ausschliesslich auf den Satistikteil."""
    @abstractmethod
    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        pass


class StatistikfilterPruefen(SatistikfilterStrategie):
    """Teste, ob angegebene Statistik zur angegebenen Zeit getestet werden muss. True=>Ja, False->Noch nicht"""
    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        return (stat_manager.statistiken[frage].modus == StatModus.PRUEFEN
                and stat_manager.statistiken[frage].ist_abzufragen(StatModus.PRUEFEN, vergleichszeit))


class StatistikfilterNeue(SatistikfilterStrategie):
    """Teste, ob angegebene Statistik zur Vergleichszeit in eine Abfrageliste fuer neue Karten kommt.
        Dies haengt auch vom Ergebnis der vorherigen Statistik ab. True->Ja, False->Noch nicht"""
    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        aktuelle_statistik = stat_manager.statistiken[frage]
        zeitdauer = 14 * 86400000  # 1 Tag = 86400000 ms
        vorherige_statistik = stat_manager.statistiken[
            Frageeinheit.vorherige_frageeinheit(frage)] if not Frageeinheit.ist_erste_frageeinheit(frage)\
            else None
        return (aktuelle_statistik.modus == StatModus.NEU
                and StatistikCalculations.berechne_millisekunden(vorherige_statistik) > zeitdauer
                and vorherige_statistik.letztes_datum() < vergleichszeit
                and vorherige_statistik.modus == StatModus.PRUEFEN
                ) if vorherige_statistik else aktuelle_statistik.modus == StatModus.NEU


class StatistikfilterLernen(SatistikfilterStrategie):
    """Teste, ob angegebene Statistik zur Vergleichszeit in eine Lernliste fuer Karten im Lernmodus kommt."""
    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        return (stat_manager.statistiken[frage].modus == StatModus.LERNEN
                and stat_manager.statistiken[frage].ist_abzufragen(StatModus.LERNEN, vergleichszeit))


class StatistikfilterLernenAlle(SatistikfilterStrategie):
    """Teste, ob angegebene Satistik Lernmodus ist. Unabhaengig von vergleichszeit.
        Dient zum Ermitteln der Gesamtzahl aller zu lernenden Vokabeln."""
    def filter(self, stat_manager: StatistikManager, frage: Type[Frageeinheit], vergleichszeit: int) -> bool:
        return stat_manager.statistiken[frage].modus == StatModus.LERNEN
