from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Type, TYPE_CHECKING

from src.classes.kartenfilter import (KartenfilterStrategie, FilterKartenstatistik, FilterVokabelbox, KartenfilterTupel,
                                      FilterKartenanzahl, FilterMischen)
from src.classes.statistikfilter import StatistikfilterPruefen
from src.repositories.vokabelkarten_repository import VokabelkartenRepository
from src.repositories.vokabelbox_repository import VokabelboxRepository
import src.utils.utils_klassen as u_klassen

if TYPE_CHECKING:
    from src.classes.vokabelbox import Vokabelbox
    from src.classes.vokabelkarte import Vokabelkarte


@dataclass(frozen=True)
class VokabeltrainerModell:
    vokabelboxen: VokabelboxRepository = field(default_factory=VokabelboxRepository)
    vokabelkarten: VokabelkartenRepository = field(default_factory=VokabelkartenRepository)
    index_aktuelle_box: int = 0

    def aktuelle_box(self) -> Vokabelbox:
        return self.vokabelboxen.vokabelboxen[self.index_aktuelle_box]

    def alle_vokabelkarten(self) -> list[Vokabelkarte]:
        return self.vokabelkarten.vokabelkarten

    def starte_vokabeltest(self, test_funktion: Callable[[Vokabelkarte], Vokabelkarte],
                           zeit: int, max_anzahl: int = 20) -> list[tuple[Vokabelkarte, Vokabelkarte]]:
        filter_liste = [
            KartenfilterTupel(funktion=FilterVokabelbox(vokabelbox=self.aktuelle_box()).filter),
            KartenfilterTupel(funktion=FilterKartenstatistik(strategie=StatistikfilterPruefen,
                                                             vokabelbox=self.aktuelle_box(),
                                                             zeit=zeit).filter),
            KartenfilterTupel(funktion=FilterKartenanzahl(max_anzahl=max_anzahl).filter),
            KartenfilterTupel(funktion=FilterMischen().filter)
        ]
        return list(map(lambda karte: (karte, test_funktion(karte)),
                        KartenfilterStrategie.filter_karten(filter_liste, self.alle_vokabelkarten())))  # 5. Testen

    @staticmethod
    def datum_der_letzten_antwort() -> int:
        """Ergebniss in Millisekunden
            Die Lernuhr sollte nicht weiter als die letzte Antwort zurueckgedreht werden, da es sonst zu Antworten
            mit gleichen Werten in Antwort.erzeugt()"""
        from src.classes.antwort import Antwort
        return max([antwort.erzeugt for antwort in u_klassen.suche_alle_instanzen_einer_klasse(Antwort)])
