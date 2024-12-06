from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.classes.lerninfos import Lerninfos
from src.classes.vokabelbox import Vokabelbox
from src.classes.kartenfilter import FilterVokabelbox

if TYPE_CHECKING:
    from src.classes.vokabelkarte import Vokabelkarte


@dataclass(frozen=True)
class InfoManager:
    """Klasse mit der factory-Funktion erzeugen"""
    boxen: list[Lerninfos] = field(default_factory=list)

    def erzeuge_alle_infos(self, uhrzeit: int) -> InfoManager:
        return InfoManager(boxen=[l_info.erzeuge_info_dict(uhrzeit) for l_info in self.boxen])

    def suche_karte(self, karte: Vokabelkarte) -> list[Lerninfos]:
        return [lerninfo for lerninfo in self.boxen if karte in list(lerninfo.karten)]

    @classmethod
    def factory(cls, liste_der_boxen: list[Vokabelbox], liste_der_karten: list[Vokabelkarte]) -> cls:
        """Erzeuge ein InfoManager-Objekt"""
        konvertierte_boxen = list(map(
            lambda box: Lerninfos(box=box, karten=FilterVokabelbox(vokabelbox=box).filter(liste_der_karten)),
            liste_der_boxen))
        return cls(boxen=konvertierte_boxen)
