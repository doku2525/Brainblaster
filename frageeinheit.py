from __future__ import annotations
from typing import Type, Self
from abc import ABC, abstractmethod
from dataclasses import dataclass
# from lerneinheit import Lerneinheit


@dataclass(frozen=True)
class Frageeinheit:
    rank = 1
    lerneinheit = ''
    warte_sekunden_auf_antwort = 3

    def __lt__(self, other: Frageeinheit) -> bool:
        return self.rank < other.rank

    def frage(self, lerneinheit: Lerneinheit) -> str: return ""

    def antwort(self, lerneinheit: Lerneinheit) -> str: return ""

    def titel(self) -> str: return self.__class__.__name__.replace("Frageeinheit", "")

    @staticmethod
    def alle_frageeinheiten() -> list[Type[Frageeinheit]]:
        """Suche alle Subclassen von Frageeinheit"""
        return [cls for cls in Frageeinheit().__class__.__subclasses__()]

    @staticmethod
    def suche_frageeinheiten_der_lernklasse(lernklasse: Type[Lerneinheit]) -> list[Type[Frageeinheit]]:
        """
        Liefer alle Klassen von Frageeinheiten nach rank sortiert, die zur Lerneinheit gehoeren.
        :param lernklasse:
        :return: list[Type[Frageeinheit]]
        """
        def filter_funktion(elem: Type[Frageeinheit]) -> bool:
            return "Lerneinheit"+elem().lerneinheit == lernklasse.__name__
        result = [elem for elem in Frageeinheit.alle_frageeinheiten() if filter_funktion(elem)]
        return sorted(result, key=lambda a: a().rank)

    @staticmethod
    def suche_frageeinheiten_mit_gleicher_lerneinheit(frageklasse: Type[Frageeinheit]) -> list[Type[Frageeinheit]]:
        # liefer alle Frageeinheiten nach rank sortiert, die den gleichen Namen wie frageklasse haben.
        liste_der_frageeinheiten = [frage_klasse
                                    for frage_klasse
                                    in Frageeinheit.alle_frageeinheiten()
                                    if frage_klasse().lerneinheit == frageklasse().lerneinheit]
        return sorted(liste_der_frageeinheiten, key=lambda klasse: klasse().rank)

    @staticmethod
    def suche_frageeinheit_fuer_lernklasse_mit_titel(lernklasse: Type[Lerneinheit],
                                                     titel_frageeinheit: str) -> Frageeinheit:
        """Liefer die Frageeinheit, mit dem Titel fTitel, die zur Subklasse von Lerneinheit gehoert"""
        # TODO Ersetze lambda-filter_funktion durch definierte Funktion im Typeannotation
        def filter_funktion(elem: Type[Frageeinheit]) -> bool:
            return "Frageeinheit" + titel_frageeinheit == elem.__name__
#        filter_funktion = lambda elem: "Frageeinheit" + titel_frageeinheit == elem.__name__
        return list(filter(filter_funktion, Frageeinheit.suche_frageeinheiten_der_lernklasse(lernklasse)))[0]

    @staticmethod
    def ist_erste_frageeinheit(frageklasse: Type[Frageeinheit]) -> bool:
        liste_der_frageklassen = Frageeinheit.suche_frageeinheiten_mit_gleicher_lerneinheit(frageklasse)
        return liste_der_frageklassen[0] == frageklasse

    @staticmethod
    def ist_letzte_frageeinheit(frageklasse: Type[Frageeinheit]) -> bool:
        liste_der_frageklassen = Frageeinheit.suche_frageeinheiten_mit_gleicher_lerneinheit(frageklasse)
        return liste_der_frageklassen[-1] == frageklasse

    @staticmethod
    def vorherige_frageeinheit(frageklasse: Type[Frageeinheit]) -> Type[Frageeinheit]:
        """ Wenn frageeinheit die Erste ist, dann liefert vorherige_frageeinheit() die Letzte"""
        liste_der_frageklassen = Frageeinheit.suche_frageeinheiten_mit_gleicher_lerneinheit(frageklasse)
        current_index = [index
                         for index, frage_klasse_tmp
                         in enumerate(liste_der_frageklassen)
                         if frage_klasse_tmp == frageklasse][0]
        return liste_der_frageklassen[current_index - 1]

    @staticmethod
    def folgende_frageeinheit(frageklasse: Type[Frageeinheit]) -> Type[Frageeinheit]:
        """ Wenn frageeinheit die Erste ist, dann liefert vorherige_frageeinheit() die Letzte"""
        liste_der_frageklassen = Frageeinheit.suche_frageeinheiten_mit_gleicher_lerneinheit(frageklasse)
        current_index = [index
                         for index, frage_klasse_tmp
                         in enumerate(liste_der_frageklassen)
                         if frage_klasse_tmp == frageklasse][0]
        if current_index + 1 == len(liste_der_frageklassen):
            return liste_der_frageklassen[0]
        else:
            return liste_der_frageklassen[current_index + 1]


@dataclass(frozen=True)
class FrageeinheitStandardBeschreibung(Frageeinheit):
    rank = 1
    lerneinheit = 'Standard'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung


class FrageeinheitStandardEintrag(Frageeinheit):
    rank = 2
    lerneinheit = 'Standard'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag


class FrageeinheitJapanischBedeutung(Frageeinheit):
    rank = 1
    lerneinheit = 'Japanisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung


class FrageeinheitJapanischLesung(Frageeinheit):
    rank = 2
    lerneinheit = 'Japanisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.lesung


class FrageeinheitJapanischEintrag(Frageeinheit):
    rank = 3
    lerneinheit = 'Japanisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.lesung


class FrageeinheitJapanischSchreiben(Frageeinheit):
    rank = 4
    lerneinheit = 'Japanisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return "[" + lerneinheit.lesung + "]\n" + lerneinheit.beschreibung
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag


class FrageeinheitJapanischKanjiBedeutung(Frageeinheit):
    rank = 1
    lerneinheit = 'JapanischKanji'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung


class FrageeinheitJapanischKanjiOnLesung(Frageeinheit):
    rank = 2
    lerneinheit = 'JapanischKanji'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.onLesung


class FrageeinheitJapanischKanjiKunLesung(Frageeinheit):
    rank = 3
    lerneinheit = 'JapanischKanji'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.kunLesung


class FrageeinheitJapanischKanjiSchreiben(Frageeinheit):
    rank = 4
    lerneinheit = 'JapanischKanji'

    def frage(self, lerneinheit: Lerneinheit) -> str:
        return "[" + lerneinheit.onLesung + "]\n/" + lerneinheit.kunLesung + "/\n\t" + lerneinheit.beschreibung

    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag


class FrageeinheitChinesischBedeutung(Frageeinheit):
    rank = 1
    lerneinheit = 'Chinesisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung


class FrageeinheitChinesischPinyin(Frageeinheit):
    rank = 2
    lerneinheit = 'Chinesisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.pinyin


class FrageeinheitChinesischEintrag(Frageeinheit):
    rank = 3
    lerneinheit = 'Chinesisch'

    def frage(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.beschreibung
    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.pinyin


class FrageeinheitChinesischSchreiben(Frageeinheit):
    rank = 4
    lerneinheit = 'Chinesisch'

    def frage(self, lerneinheit: Lerneinheit) -> str:
        return lerneinheit.beschreibung + "\n[" + lerneinheit.pinyin + "]"

    def antwort(self, lerneinheit: Lerneinheit) -> str: return lerneinheit.eintrag
