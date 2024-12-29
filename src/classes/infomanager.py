from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.classes.lerninfos import Lerninfos
from src.classes.vokabelbox import Vokabelbox
from src.classes.kartenfilter import FilterVokabelbox

if TYPE_CHECKING:
    from src.classes.vokabelkarte import Vokabelkarte


"""Die Klasse soll spaeter die Aktuallisierung der Boxen managen, damit nicht bei jeder Anederung alle Boxen
neu Berechnet werden. Wenn es eine Karte bekommt, dann sucht es die Boxen, die neu berechnet werden muesssen und
fuehrt die Neuberechnung nur fuer diese Box aus."""


@dataclass(frozen=True)
class InfoManager:
    """Klasse mit der factory-Funktion erzeugen"""
    boxen: list[Lerninfos] = field(default_factory=list)

    def erzeuge_alle_infos(self, uhrzeit: int) -> InfoManager:
        """Rufe die erzeuge_info_dict(uhrzeit) fuer jedes Element der Liste BOXEN, also Vokabelboxen, aus."""
        return InfoManager(boxen=[lern_info.erzeuge_infos(uhrzeit) for lern_info in self.boxen])

    def update_infos_fuer_karte(self, alte_karte: Vokabelkarte, neue_karte: Vokabelkarte, uhrzeit: int) -> InfoManager:
        veraenderte_boxen = self.suche_karte(alte_karte)
        return InfoManager(
            boxen=[box if box not in veraenderte_boxen else box.ersetze_karte(alte_karte, neue_karte, uhrzeit)
                   for box
                   in self.boxen])

    def suche_karte(self, karte: Vokabelkarte) -> list[Lerninfos]:
        """Suche alle Vokabelboxen der Liste, also Lerninfos, in denen die Vokabelkarte KARTE steckt."""
        return [lerninfo for lerninfo in self.boxen if karte in list(lerninfo.karten)]

    def boxen_als_number_dict(self) -> list[dict[str, dict[str: dict[str: int]]]]:
        """Liefer Liste, in der jede Lerneinheit durch ein Dictionary mit dem Statistikzahlen fuer jede Frageeinheit"""
        return [{frage_einheit.__name__: lern_info.infos[frage_einheit].as_number_dict()
                 for frage_einheit
                 in lern_info.infos.keys()} for lern_info in self.boxen]

    @classmethod
    def factory(cls, liste_der_boxen: list[Vokabelbox], liste_der_karten: list[Vokabelkarte]) -> cls:
        """Erzeuge ein InfoManager-Objekt. Sollte im Normalfall mit der Vokabelbox und der Kartenliste aus dem
        Repository aufgerufen werden."""
        konvertierte_boxen = list(map(
            lambda box: Lerninfos(box=box, karten=FilterVokabelbox(vokabelbox=box).filter(liste_der_karten)),
            liste_der_boxen))
        return cls(boxen=konvertierte_boxen)
