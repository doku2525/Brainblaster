from __future__ import annotations
from collections import namedtuple
from dataclasses import dataclass, field
from functools import reduce
import random
from typing import Callable, Type, TYPE_CHECKING

from src.classes.kartenfilter import FilterKartenstatistik, FilterVokabelbox, KartenfilterTupel
import src.classes.kartenfilter as kfilter
from src.classes.statistikfilter import StatistikfilterPruefen
from src.repositories.vokabelkarten_repository import VokabelkartenRepository
from src.repositories.vokabelbox_repository import VokabelboxRepository

if TYPE_CHECKING:
    from src.classes.vokabelbox import Vokabelbox
    from src.classes.vokabelkarte import Vokabelkarte

"""
Im original ist Vokabeltrainer von OrderedCollection abgeleitet und speichert die Vojkabelboxen
Dazu eine instance Variable current Index.
Die Methoden greifen vor allem auf die Liste zu, veraendern den Index.
Ausserdem FileOut- und FileIn-Funktionen 

Funtkion fuer Zeit
(datetime.datetime.now().timestamp()*1000,datetime.datetime.fromisoformat('2024-07-07 02:22:58').timestamp()*1000)
"""
# TODO Issue #8 Speicher und Lade den aktuellenIndex und die aktuellenFrageeinheiten in den Vokabelboxen
# TODO Issue #8 Momentan gibt es noch keine Verwendung der LernUhr.
# Funktionen nach Aufgabe:
# Vokabelbox:
# x  titelAllerVokabelboxen(self) -> list[str]:  !!! Wird in main.py aufgerufen                            xxx VokabelboxRepository
# x  addVokabelbox(self, vokBox) -> Vokabeltrainer:  !!! Wird in vielen ImporterKlassen aufgerufen         xxx VokabelboxRepository
# x  speicherVokabelboxInDatei(self):   !!! Wird in main.py und ImporterKlassen aufgerufen                 xxx VokabelboxRepository
# x  ladeVokabelboxenAusDatei(self):   !!! Wird in main.py, webApp_main.py und ImporterKlassen aufgerufen  xxx VokabelboxRepository
# statische Methoden:
#    neu() -> Vokabeltrainer:
# Klassenmethoden:
#    addBeispiele(cls, anzahl, sprache) -> None:
# x  addVokabelkarte(cls, karte) -> None:                               xxx VokabelkartenRepository
# x  speicherVokabelkartenInDatei(cls) -> None:                         xxx VokabelkartenRepository
# x  ladeVokabelkartenAusDatei(cls) -> None:                            xxx VokabelkartenRepository


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
        zu_testende_karten = kfilter.filter_karten(filter_liste, self.alle_vokabelkarten())  # 3. Filter
        ersten_x_karten = random.sample(zu_testende_karten[:20],
                                        len(zu_testende_karten[:20]))           # 4. Begrenze auf x Karten und mische
        return list(map(lambda karte: (karte, test_funktion(karte)), ersten_x_karten))  # 5. Fuehre Test durch
