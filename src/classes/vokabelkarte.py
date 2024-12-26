from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Type, TYPE_CHECKING

from src.classes.statistikmanager import StatistikManager
from src.classes.lerneinheit import Lerneinheit, LerneinheitFactory
import src.utils.utils_enum as utils_enum

if TYPE_CHECKING:
    from src.classes.frageeinheit import Frageeinheit
    from src.classes.antwort import Antwort


class KartenStatus(Enum):
    NORMAL = 0
    GESPERT = 1
    EXPORTIERT = 2
    GEANDERT = 3
    MEMO = 4
    UEBERPRUEFEN = 5


@dataclass(frozen=True)
class Vokabelkarte:
    lerneinheit: Lerneinheit = field(default_factory=Lerneinheit)
    lernstats: StatistikManager = field(default_factory=StatistikManager)
    erzeugt: int = 0
    status: KartenStatus = field(default=KartenStatus.NORMAL)

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        # Um die Lerneinheit rekonstruieren zu koennen wird das Feld lernklasse von mein_asdict() hinzugefuegt.
        return cls(lerneinheit=Lerneinheit.fromdict(source_dict['lerneinheit'],
                                                    klassenname=source_dict.get('lernklasse', None)),
                   lernstats=StatistikManager.fromdict(source_dict['lernstats']),
                   erzeugt=source_dict['erzeugt'],
                   status=utils_enum.name_zu_enum(source_dict['status'], KartenStatus))

    def erzeuge_statistik(self) -> Vokabelkarte:
        return Vokabelkarte(self.lerneinheit,
                            StatistikManager.erzeuge(self.lerneinheit.__class__),
                            self.erzeugt,
                            self.status)

    def neue_antwort(self, frage_einheit: Type[Frageeinheit], antwort: Antwort) -> Vokabelkarte:
        return replace(self,
                       lernstats=self.lernstats.update_statistik_mit_antwort(frageeinheit=frage_einheit,
                                                                             antwort=antwort))

    @staticmethod
    def erzeugeBeispiele(liste: list[Lerneinheit]) -> list[Vokabelkarte]:
        if not liste:
            return []
        else:
            return [Vokabelkarte(lern_einheit, StatistikManager(), 0, KartenStatus.NORMAL).erzeuge_statistik()
                    for lern_einheit
                    in liste]

    @staticmethod
    def lieferBeispielKarten(anzahl: int, sprache: str) -> list[Vokabelkarte]:
        if sprache == "Japanisch":
            return Vokabelkarte.erzeugeBeispiele(LerneinheitFactory.erzeuge_japanisch_beispiele(anzahl))
        if sprache == "Kanji":
            return Vokabelkarte.erzeugeBeispiele(
                LerneinheitFactory.erzeuge_japanisch_kanji_beispiele(anzahl))
        if sprache == "Chinesisch":
            return Vokabelkarte.erzeugeBeispiele(LerneinheitFactory.erzeuge_chinesisch_beispiele(anzahl))
        else:
            return Vokabelkarte.erzeugeBeispiele(LerneinheitFactory.erzeuge_standard_beispiele(anzahl))
