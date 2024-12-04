from __future__ import annotations
from typing import Callable, Type, TYPE_CHECKING

from src.classes.kartenfilter import (KartenfilterStrategie, KartenfilterTupel, FilterVokabelbox,
                                      FilterKartenstatistik, FilterKartenanzahl, FilterMischen)
from src.classes.statistikfilter import (StatistikfilterPruefen, StatistikfilterLernen, StatistikfilterLernenAlle,
                                         StatistikfilterNeue, StatistikfilterNeueAlle)


class FilterlistenFactory:

    @staticmethod
    def filter_und_execute(funktion: Callable[[Vokabelkarte], Vokabelkarte] | None,
                           filter_liste: list[KartenfilterTupel],
                           liste_der_vokabeln: list[Vokabelkarte]
                           ) -> list[tuple[Vokabelkarte, Vokabelkarte]] | list[Vokabelkarte]:
        """ Wenn funktion None ist, dann wird einfach nur gefiltert ohne die Funtkion auszufuehren"""
        return list(map(lambda karte: (karte, funktion(karte)) if funktion else karte,
                        KartenfilterStrategie.filter_karten(filter_liste, liste_der_vokabeln)))

    @staticmethod
    def filterliste_genericstatistik(strategie: Type[SatistikfilterStrategie],
                                     zeit: int, max_anzahl: int,
                                     vokabelbox: Vokabelbox) -> list[KartenfilterTupel]:
        return [
            KartenfilterTupel(funktion=FilterVokabelbox(vokabelbox=vokabelbox).filter),
            KartenfilterTupel(funktion=FilterKartenstatistik(strategie=strategie,
                                                             vokabelbox=vokabelbox,
                                                             zeit=zeit).filter),
            KartenfilterTupel(funktion=FilterKartenanzahl(max_anzahl=max_anzahl).filter),
            KartenfilterTupel(funktion=FilterMischen().filter)
        ]

    @classmethod
    def filterliste_vokabeln_pruefen(cls, vokabelbox: Vokabelbox, zeit: int,
                                     max_anzahl: int = 20) -> list[KartenfilterTupel]:
        return cls.filterliste_genericstatistik(strategie=StatistikfilterPruefen,
                                                zeit=zeit,
                                                max_anzahl=max_anzahl,
                                                vokabelbox=vokabelbox)

    @classmethod
    def filterliste_vokabeln_lernen(cls, vokabelbox: Vokabelbox, zeit: int,
                                    max_anzahl: int = 20) -> list[KartenfilterTupel]:
        return cls.filterliste_genericstatistik(strategie=StatistikfilterLernen,
                                                zeit=zeit,
                                                max_anzahl=max_anzahl,
                                                vokabelbox=vokabelbox)

    @classmethod
    def filterliste_vokabeln_neue(cls, vokabelbox: Vokabelbox, zeit: int = 0,
                                  max_anzahl: int = 10) -> list[KartenfilterTupel]:
        return cls.filterliste_genericstatistik(strategie=StatistikfilterNeue,
                                                zeit=zeit,
                                                max_anzahl=max_anzahl,
                                                vokabelbox=vokabelbox)
