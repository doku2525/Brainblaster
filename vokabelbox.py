from __future__ import annotations
from typing import Iterable, Type
import random

import abfragefilter
import statistik
from vokabelkarte import Vokabelkarte
from frageeinheit import Frageeinheit
from lerneinheit import Lerneinheit

""" Das Attribut selektor enthaelt eine Liste mit Strings, die Tests enthalten, welche durch eval() ausgwertet werden.
Zum Beispiel: ('satz', True) in a.lerneinheit.daten.items()"""
# TODO Ein Weg finden, keine Strings mit eval() verwenden zu muessen.


class Vokabelbox:
    # TODO Definiere als @datacalss
    def __init__(self, titel: str, lernklasse: Type[Lerneinheit], selektor: list[str],
                 aktuelle_frage: Type[Frageeinheit] = None):
        self.titel: str = titel
        self.lernklasse: Type[Lerneinheit] = lernklasse
        self.selektor: list[str] = selektor
        self.aktuelleFrage: Type[Frageeinheit] = self.verfuegbare_frageeinheiten()[0] if not aktuelle_frage else aktuelle_frage

    def __lt__(self, other):
        return self.titel < other.titel

    def rename(self, titel: str) -> Vokabelbox:
        return Vokabelbox(titel, self.lernklasse, self.selektor)

    def verfuegbare_frageeinheiten(self) -> list[Type[Frageeinheit]]:
        # TODO Die Methode koennte evtl. als privat markiert werden?
        #  Scheint nur eine Hilfsfunktion fuer die folgenden Methoden zu sein
        return Frageeinheit.suche_frageeinheiten_der_lernklasse(self.lernklasse)

    # def ist_erste_frageeinheit(self) -> bool:
    #     current_index = [index
    #                      for index, frage_klasse
    #                      in enumerate(self.verfuegbare_frageeinheiten())
    #                      if frage_klasse == self.aktuelleFrage][0]
    #     return current_index == 0

    # def ist_letzte_frageeinheit(self) -> bool:
    #     current_index = [index
    #                      for index, frage_klasse
    #                      in enumerate(self.verfuegbare_frageeinheiten())
    #                      if frage_klasse == self.aktuelleFrage][0]
    #     return current_index + 1 == len(self.verfuegbare_frageeinheiten())

    # def naechste_frageeinheit(self) -> Vokabelbox:
    #     """ Wenn die aktuelle Frageeinheit die Letzte ist, dann liefert die naechste_frageeinheit() die Erste"""
    #     current_index = [index
    #                      for index, frage_klasse
    #                      in enumerate(self.verfuegbare_frageeinheiten())
    #                      if frage_klasse == self.aktuelleFrage][0]
    #     if current_index + 1 == len(self.verfuegbare_frageeinheiten()):
    #         return Vokabelbox(self.titel, self.lernklasse, self.selektor, self.verfuegbare_frageeinheiten()[0])
    #     else:
    #         return Vokabelbox(self.titel, self.lernklasse,
    #                           self.selektor, self.verfuegbare_frageeinheiten()[current_index + 1])

    # def vorherige_frageeinheit(self) -> Vokabelbox:
    #     """ Wenn die aktuelle Frageeinheit die Erste ist, dann liefert die vorherige_frageeinheit() die Letzte"""
    #     current_index = [index
    #                      for index, frage_klasse
    #                      in enumerate(self.verfuegbare_frageeinheiten())
    #                      if frage_klasse == self.aktuelleFrage][0]
    #     return Vokabelbox(self.titel, self.lernklasse, self.selektor,
    #                       self.verfuegbare_frageeinheiten()[current_index - 1])

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
        # TODO Die for-Schleife koennte vielleicht in eine Funktion ausgelagert werden oder mit Listcomprehension geschrieben werden?
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
                                      if stats.statistiken[self.aktuelleFrage].modus == statmod])
        result["zuPruefen"] = len([stats
                                   for stats
                                   in liste_der_statistikmanager_der_karten
                                   if abfragefilter.PruefenFilter().filter(stats, self.aktuelleFrage, uhrzeit)])
        result["zuLernen"] = len([stats
                                  for stats
                                  in liste_der_statistikmanager_der_karten
                                  if abfragefilter.LernenFilter().filter(stats, self.aktuelleFrage, uhrzeit)])
        result["zuNeu"] = len([stats
                                  for stats
                                  in liste_der_statistikmanager_der_karten
                                  if abfragefilter.NeueFilter().filter(stats, self.aktuelleFrage, uhrzeit)])
        return result

    @staticmethod
    def mische_karten(liste_der_karten: list[Vokabelkarte]) -> list[Vokabelkarte]:
        return random.sample(liste_der_karten, len(liste_der_karten))


"""
    karte.lernstats.statistiken[trainer.aktuellerIndex.aktuelleFrage].zeitZumLernen(0)
    for karte in trainer.aktuellerIndex.filterVokabelkarten(vt.Vokabeltrainer.vokabelkarten)]

liste[0].lernstats.statistiken[trainer.aktuellerIndex.aktuelleFrage] = liste[0].lernstats.statistiken[trainer.aktuellerIndex.aktuelleFrage]
"""