from __future__ import annotations
from typing import Iterable, Type
from dataclasses import dataclass, field
import random

import abfragefilter
import statistik
from vokabelkarte import Vokabelkarte
from frageeinheit import (Frageeinheit, FrageeinheitChinesischBedeutung, FrageeinheitChinesischEintrag,
                          FrageeinheitChinesischPinyin, FrageeinheitChinesischSchreiben, FrageeinheitJapanischSchreiben,
                          FrageeinheitJapanischEintrag, FrageeinheitStandardEintrag, FrageeinheitStandardBeschreibung,
                          FrageeinheitJapanischBedeutung, FrageeinheitJapanischLesung,
                          FrageeinheitJapanischKanjiBedeutung, FrageeinheitJapanischKanjiSchreiben,
                          FrageeinheitJapanischKanjiKunLesung, FrageeinheitJapanischKanjiOnLesung)
from lerneinheit import (Lerneinheit, LerneinheitJapanisch, LerneinheitChinesisch, LerneinheitStandard,
                         LerneinheitJapanischKanji)


""" Das Attribut selektor enthaelt eine Liste mit Strings, die Tests enthalten, welche durch eval() ausgwertet werden.
Zum Beispiel: ('satz', True) in a.lerneinheit.daten.items()"""
# TODO Ein Weg finden, keine Strings mit eval() verwenden zu muessen.
# TODO Fuer die Liste von Strings mit Tests einen eigenen Datentyp erstellen


@dataclass(frozen=True)
class Vokabelbox:
    titel: str = ""
    lernklasse: Type[Lerneinheit] = None
    selektor: list[str] = field(default_factory=list)
    aktuelle_frage: Type[Frageeinheit] = None

    def __post_init__(self):
        # TODO Mit solchen Tricks zu arbeiten ist vielleicht nicht die beste Idee und ein Zeichen dafuer,
        #   am Design etwas zu veraendern.
        #   ??? Muss aktuelleFrage wirklich als Attribut gespeichert werden oder sollte es nicht eine Funktion sein?
        object.__setattr__(self,
                           'aktuelle_frage',
                           self.verfuegbare_frageeinheiten()[0] if not self.aktuelle_frage else self.aktuelle_frage)

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(titel=source_dict['titel'],
                   lernklasse=globals()[source_dict['lernklasse']],
                   selektor=[element for element in source_dict['selektor']],
                   aktuelle_frage=globals()[source_dict['aktuelle_frage']])

    def __lt__(self, other):
        return self.titel < other.titel

    def rename(self, titel: str) -> Vokabelbox:
        return Vokabelbox(titel, self.lernklasse, self.selektor)

    def verfuegbare_frageeinheiten(self) -> list[Type[Frageeinheit]]:
        """
        Liefert die Klassen von Frageeinheit, die fuer die self.lernklasse verfuegbar sind
        :return: list[Type[Frageeinheit]]
        """
        return Frageeinheit.suche_frageeinheiten_der_lernklasse(self.lernklasse)

    def ist_erste_frageeinheit(self) -> bool:
        """
        Testet, ob die aktuelle Frage die erste in der Liste der verfuegbaren Fragen ist.
        :return: bool
        """
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        return current_index == 0

    def ist_letzte_frageeinheit(self) -> bool:
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        return current_index + 1 == len(self.verfuegbare_frageeinheiten())

    def naechste_frageeinheit(self) -> Vokabelbox:
        """ Wenn die aktuelle Frageeinheit die Letzte ist, dann liefert die naechste_frageeinheit() die Erste"""
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        if current_index + 1 == len(self.verfuegbare_frageeinheiten()):
            return Vokabelbox(self.titel, self.lernklasse, self.selektor, self.verfuegbare_frageeinheiten()[0])
        else:
            return Vokabelbox(self.titel, self.lernklasse,
                              self.selektor, self.verfuegbare_frageeinheiten()[current_index + 1])

    def vorherige_frageeinheit(self) -> Vokabelbox:
        """ Wenn die aktuelle Frageeinheit die Erste ist, dann liefert die vorherige_frageeinheit() die Letzte"""
        current_index = [index
                         for index, frage_klasse
                         in enumerate(self.verfuegbare_frageeinheiten())
                         if frage_klasse == self.aktuelle_frage][0]
        return Vokabelbox(self.titel, self.lernklasse, self.selektor,
                          self.verfuegbare_frageeinheiten()[current_index - 1])

    def filter_vokabelkarten(self, kartenliste: list[Vokabelkarte]) -> list[Vokabelkarte]:
        karten_der_lernklasse = [karte for karte in kartenliste if karte.lerneinheit.__class__ is self.lernklasse]

        def filter_rekursiv(result: Iterable[Vokabelkarte], filter_funcs: list[str]):
            """Die Filterfunktionen sind als String gespeichert, um sie mit einem Texteditor bearbeiten zu koennen"""
            if not filter_funcs:
                return result
            else:
                return filter_rekursiv(filter(lambda a: eval(filter_funcs[0]), result), filter_funcs[1:])
        return filter_rekursiv(karten_der_lernklasse, self.selektor)

    def sammle_infos(self, alle_vokabelkarten: list[Vokabelkarte], uhrzeit: int) -> dict[str, int]:
        # TODO Die for-Schleife koennte vielleicht in eine Funktion ausgelagert werden
        #  oder mit Listcomprehension geschrieben werden?
        result = {}
        karten_dieser_vokabelbox = list(self.filter_vokabelkarten(alle_vokabelkarten))
        liste_der_statistikmanager_der_karten = [karte.lernstats
                                                 for karte
                                                 in karten_dieser_vokabelbox]
        result["karten"] = len(karten_dieser_vokabelbox)
        for statmod in statistik.StatModus:
            result_key = str(statmod).replace("StatModus.", "")
            result[result_key] = len([stats
                                      for stats
                                      in liste_der_statistikmanager_der_karten
                                      if stats.statistiken[self.aktuelle_frage].modus == statmod])
        result["zuPruefen"] = len([stats
                                   for stats
                                   in liste_der_statistikmanager_der_karten
                                   if abfragefilter.PruefenFilter().filter(stats, self.aktuelle_frage, uhrzeit)])
        result["zuLernen"] = len([stats
                                  for stats
                                  in liste_der_statistikmanager_der_karten
                                  if abfragefilter.LernenFilter().filter(stats, self.aktuelle_frage, uhrzeit)])
        result["zuNeu"] = len([stats
                               for stats
                               in liste_der_statistikmanager_der_karten
                               if abfragefilter.NeueFilter().filter(stats, self.aktuelle_frage, uhrzeit)])
        return result

    @staticmethod
    def mische_karten(liste_der_karten: list[Vokabelkarte]) -> list[Vokabelkarte]:
        return random.sample(liste_der_karten, len(liste_der_karten))


"""
    karte.lernstats.statistiken[trainer.aktuellerIndex.aktuelleFrage].zeitZumLernen(0)
    for karte in trainer.aktuellerIndex.filterVokabelkarten(vt.Vokabeltrainer.vokabelkarten)]

liste[0].lernstats.statistiken[trainer.aktuellerIndex.aktuelleFrage] = liste[0].lernstats.statistiken[trainer.aktuellerIndex.aktuelleFrage]
"""