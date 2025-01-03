from __future__ import annotations
from abc import ABC
from dataclasses import dataclass, field
import datetime
from src.classes.lernuhr import Lernuhr
from src.classes.statistik import StatistikCalculations
from src.classes.vokabelkarte import Vokabelkarte
import src.utils.utils_klassen as u_k


@dataclass(frozen=True)
class DisplayPatternVokabelkarte:

    lerneinheit: list[str] = field(default_factory=list)
    statistiken: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def in_vokabel_liste(cls, vokabelkarte: Vokabelkarte) -> DisplayPatternVokabelkarte:
        display_klasse = u_k.suche_subklasse_by_klassenname(
            cls, f"DisplayPatternVokabelkarte{vokabelkarte.lerneinheit.__class__.__name__}")

        return DisplayPatternVokabelkarte(
            lerneinheit=display_klasse.display_lerneinheit_in_liste(vokabelkarte),
            statistiken=cls.display_statistik(vokabelkarte)
        ) if display_klasse else DisplayPatternVokabelkarte()

    @staticmethod
    def display_statistik(vokabelkarte: Vokabelkarte) -> dict[str, dict[str, str]]:
        return {klasse().titel(): {"ef": "%.2f" % StatistikCalculations.ef(stat),
                                   "folge": " ".join([str(x.antwort) for x in stat.antworten[-5:]]),
                                   "next": datetime.datetime.fromtimestamp(
                                        int(stat.naechstes_datum() / 1000)).strftime("%y-%m-%d %H:%M"),
                                   "last": datetime.datetime.fromtimestamp(
                                        int(stat.antworten[-1].erzeugt / 1000)).strftime("%y-%m-%d %H:%M")}
                for klasse, stat in vokabelkarte.lernstats.statistiken.items()
                if stat.antworten}


class DisplayPatternVokabelkarteLerneinheitChinesisch(DisplayPatternVokabelkarte):

    @staticmethod
    def display_lerneinheit_in_liste(vokabelkarte: Vokabelkarte) -> list[str]:
        return [vokabelkarte.lerneinheit.eintrag,
                vokabelkarte.lerneinheit.traditionell,
                vokabelkarte.lerneinheit.pinyin,
                vokabelkarte.lerneinheit.beschreibung]


class DisplayPatternVokabelkarteLerneinheitJapanisch(DisplayPatternVokabelkarte):

    @staticmethod
    def display_lerneinheit_in_liste(vokabelkarte: Vokabelkarte) -> list[str]:
        return [vokabelkarte.lerneinheit.eintrag,
                vokabelkarte.lerneinheit.lesung,
                vokabelkarte.lerneinheit.beschreibung]


class DisplayPatternVokabelkarteLerneinheitJapanischKanji(DisplayPatternVokabelkarte):

    @staticmethod
    def display_lerneinheit_in_liste(vokabelkarte: Vokabelkarte) -> list[str]:
        return [vokabelkarte.lerneinheit.eintrag,
                vokabelkarte.lerneinheit.on_lesung,
                vokabelkarte.lerneinheit.kun_lesung,
                vokabelkarte.lerneinheit.beschreibung]
