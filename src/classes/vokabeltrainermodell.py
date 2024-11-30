from __future__ import annotations
from collections import namedtuple
from dataclasses import dataclass, field
from functools import reduce
import random
from typing import Callable, Type, TYPE_CHECKING

from src.classes.kartenfilter import FilterKartenstatistik, FilterVokabelbox, KartenfilterTupel, KartenfilterStrategie
from src.classes.statistikfilter import StatistikfilterPruefen
from src.repositories.vokabelkarten_repository import VokabelkartenRepository
from src.repositories.vokabelbox_repository import VokabelboxRepository

if TYPE_CHECKING:
    from src.classes.vokabelbox import Vokabelbox
    from src.classes.vokabelkarte import Vokabelkarte


@dataclass
class VokabeltrainerModell:
    vokabelboxen: VokabelboxRepository = field(default_factory=VokabelboxRepository)
    vokabelkarten: VokabelkartenRepository = field(default_factory=VokabelkartenRepository)
    index_aktuelle_box: int = 0

    def aktuelle_box(self) -> Vokabelbox:
        return self.vokabelboxen.vokabelboxen[self.index_aktuelle_box]

    def alle_vokabelkarten(self) -> list[Vokabelkarte]:
        return self.vokabelkarten.vokabelkarten

    def starte_vokabeltest(self, test_funktion: Callable[[Vokabelkarte], Vokabelkarte],
                           zeit: int) -> list[tuple[Vokabelkarte, Vokabelkarte]]:
        filter_liste = [
            KartenfilterTupel(funktion=FilterVokabelbox(self.aktuelle_box())),
            KartenfilterTupel(funktion=FilterKartenstatistik(StatistikfilterPruefen, self.aktuelle_box(), zeit))]
        zu_testende_karten = KartenfilterStrategie.filter_karten(filter_liste, self.alle_vokabelkarten())  # 3. Filter
        ersten_x_karten = random.sample(zu_testende_karten[:20],
                                        len(zu_testende_karten[:20]))           # 4. Begrenze auf x Karten und mische
        return list(map(lambda karte: (karte, test_funktion(karte)), ersten_x_karten))  # 5. Fuehre Test durch
