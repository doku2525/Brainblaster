from __future__ import annotations
from typing import Callable
from dataclasses import dataclass, field
import random

from src.classes.lernuhr import Lernuhr
from src.repositories.vokabelkarten_repository import VokabelkartenRepository
from src.repositories.vokabelbox_repository import (VokabelboxRepository)
from src.classes.vokabelkarte import Vokabelkarte
from src.classes.statistikfilter import StatistikfilterPruefen


"""
Im original ist Vokabeltrainer von OrderedCollection abgeleitet und speichert die Vojkabelboxen
Dazu eine instance Variable current Index.
Die Methoden greifen vor allem auf die Liste zu, veraendern den Index.
Ausserdem FileOut- und FileIn-Funktionen 

Funtkion fuer Zeit
(datetime.datetime.now().timestamp()*1000,datetime.datetime.fromisoformat('2024-07-07 02:22:58').timestamp()*1000)
"""
# TODO Issue #8 1. Implementiere VokabelRepository-Klasse um die ganze speicher und laden auszulagern.
#   Zur Zeit wird nicht in JOSN, sondern vokabelkarten.data und vokabelboxen.data geschrieben.
# TODO Issue #8 Speicher und Lade den aktuellenIndex und die aktuellenFrageeinheiten in den Vokabelboxen
# TODO Issue #8 Momentan gibt es noch keine Verwendung der LernUhr.
# TODO Issue #8 import pickle muss verschwinden
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

    def starte_vokabeltest(self,
                           filter_funktion: Callable[[Vokabelkarte], bool],
                           test_funktion: Callable[[Vokabelkarte], Vokabelkarte],
                           zeit: int) -> list[tuple[Vokabelkarte, Vokabelkarte]]:

        vok_box = self.vokabelboxen[self.index_aktuelle_box]
        karten_der_box = vok_box.filter_vokabelkarten(self.vokabelkarten)               # 1. Vokabelboxfilter
        zu_testende_karten = list(filter(                                               # 2. Pruefenfilter anwenden
            lambda karte: StatistikfilterPruefen.filter(stat_manager=karte.lernstats,
                                                        frage=vok_box.aktuelle_frage,
                                                        vergleichszeit=zeit), karten_der_box))
        zu_testende_karten = zu_testende_karten[:20]                                    # 3. Begrenze Anzahl auf x
        ersten_x_karten = random.sample(zu_testende_karten, len(zu_testende_karten))    # 4. Mische Karten
        return list(map(lambda karte: (karte, test_funktion(karte)), ersten_x_karten))  # 5. Fuehre Test durch


    # dateiKarten = "./daten/data/vokabelkarten.data"
    # dateiKartenBackup = "./daten/data/backups/vokabelkarten."
    # dateiKartenJSON = "./daten,data/vokabelkarten.json"

    # def __init__(self, vokabelrepository: VokabelkartenRepository, vokabelboxen: list[vokabelbox.Vokabelbox],
    #              aktuellerIndex: vokabelbox.Vokabelbox = None):
    #     self.vokabel_repository = vokabelrepository
    #     self.vokabelbox_repository = InMemeoryVokabelboxRepository("./data/vokabelboxen.data")
    #     self.aktuellerIndex = aktuellerIndex
    #     self.dateiBoxen = "./data/vokabelboxen.data"
    #     self.dateiBoxenJSON = "./data/vokabelboxen.json"

#    @staticmethod
#    def neu() -> VokabeltrainerModell:
#        return VokabeltrainerModell([], [])

    @classmethod
    def addBeispiele(cls, anzahl, sprache) -> None:
        # TODO Issue #8 In FactoryKlasse ausgelagern.
        # Funktion wird nur in den Tests benutzt
        [VokabeltrainerModell.addVokabelkarte(karte) for karte in Vokabelkarte.lieferBeispielKarten(anzahl, sprache)]
