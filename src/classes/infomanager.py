from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.classes.lerninfos import Lerninfos
from src.classes.vokabelbox import Vokabelbox

if TYPE_CHECKING:
    from src.classes.vokabelkarte import Vokabelkarte


@dataclass(frozen=True)
class InfoManager:
    """Klasse mit der factory-Funktion erzeugen"""
    boxen: list[Lerninfos] = field(default_factory=list)

    @classmethod
    def factory(cls, liste_der_boxen: list[Vokabelbox], liste_der_karten: list[Vokabelkarte]) -> cls:
        """Erzeuge ein InfoManager-Objekt"""
        konvertierte_boxen = list(map(lambda box: Lerninfos(box=box,
                                                            karten=box.filter_vokabelkarten(liste_der_karten)),
                                      liste_der_boxen))
        return cls(boxen=konvertierte_boxen)
