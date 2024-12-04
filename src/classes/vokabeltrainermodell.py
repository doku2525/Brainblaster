from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Type, TYPE_CHECKING

from src.classes.kartenfilter import (KartenfilterStrategie, FilterKartenstatistik, FilterVokabelbox, KartenfilterTupel,
                                      FilterKartenanzahl, FilterMischen)
from src.classes.statistikfilter import (SatistikfilterStrategie, StatistikfilterPruefen, StatistikfilterLernen,
                                         StatistikfilterNeue)
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

    def filterliste_genericstatistik(self, strategie: Type[SatistikfilterStrategie],
                                     zeit: int, max_anzahl: int,
                                     vokabelbox: Vokabelbox | None = None) -> list[KartenfilterTupel]:
        meine_vokabelbox = self.aktuelle_box() if vokabelbox is None else vokabelbox
        return [
            KartenfilterTupel(funktion=FilterVokabelbox(vokabelbox=meine_vokabelbox).filter),
            KartenfilterTupel(funktion=FilterKartenstatistik(strategie=strategie,
                                                             vokabelbox=meine_vokabelbox,
                                                             zeit=zeit).filter),
            KartenfilterTupel(funktion=FilterKartenanzahl(max_anzahl=max_anzahl).filter),
            KartenfilterTupel(funktion=FilterMischen().filter)]

    def filterliste_vokabeln_pruefen(self, zeit: int, max_anzahl: int = 20) -> list[KartenfilterTupel]:
        return self.filterliste_genericstatistik(strategie=StatistikfilterPruefen,
                                                 zeit=zeit,
                                                 max_anzahl=max_anzahl)

    def filterliste_vokabeln_lernen(self, zeit: int, max_anzahl: int = 20) -> list[KartenfilterTupel]:
        return self.filterliste_genericstatistik(strategie=StatistikfilterLernen,
                                                 zeit=zeit,
                                                 max_anzahl=max_anzahl)

    def filterliste_vokabeln_neue(self, zeit: int, max_anzahl: int = 10,
                                  vokabelbox: Vokabelbox | None = None) -> list[KartenfilterTupel]:
        return self.filterliste_genericstatistik(strategie=StatistikfilterNeue,
                                                 zeit=zeit,
                                                 max_anzahl=max_anzahl,
                                                 vokabelbox=vokabelbox)

    @staticmethod
    def filter_und_execute(funktion: Callable[[Vokabelkarte], Vokabelkarte] | None,
                           filter_liste: list[KartenfilterTupel],
                           liste_der_vokabeln: list[Vokabelkarte]
                           ) -> list[tuple[Vokabelkarte, Vokabelkarte]] | list[Vokabelkarte]:
        """ Wenn funktion None ist, dann wird einfach nur gefiltert ohne die Funtkion auszufuehren"""
        return list(map(lambda karte: (karte, funktion(karte)) if funktion else karte,
                        KartenfilterStrategie.filter_karten(filter_liste, liste_der_vokabeln)))

    @staticmethod
    def datum_der_letzten_antwort() -> int:
        """Ergebniss in Millisekunden
            Die Lernuhr sollte nicht weiter als die letzte Antwort zurueckgedreht werden, da es sonst zu Antworten
            mit gleichen Werten in Antwort.erzeugt()"""
        from src.classes.antwort import Antwort
        return max([antwort.erzeugt for antwort in u_klassen.suche_alle_instanzen_einer_klasse(Antwort)])

    @staticmethod
    def results_to_list(liste: list[tuple[Vokabelkarte, Vokabelkarte]]) -> list[Vokabelkarte]:
        return [karte for karte, _ in liste]
