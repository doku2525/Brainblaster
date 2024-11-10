from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field

import libs.utils_enum as utils_enum
from statistikmanager import StatistikManager
from lerneinheit import Lerneinheit, LerneinheitFactory


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

    # TODO Namen der Methoden von CamelFrom auf python_form umstellen
    def erzeugeStatistik(self) -> Vokabelkarte:
        return Vokabelkarte(self.lerneinheit,
                            StatistikManager.erzeuge(self.lerneinheit.__class__),
                            self.erzeugt,
                            self.status)

    @staticmethod
    def erzeugeBeispiele(liste: list[Lerneinheit]) -> list[Vokabelkarte]:
        if not liste:
            return []
        else:
            return [Vokabelkarte(lern_einheit, StatistikManager(), 0, KartenStatus.NORMAL).erzeugeStatistik()
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
