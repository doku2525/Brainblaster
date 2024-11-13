from __future__ import annotations
from dataclasses import dataclass, field

from src.repositories.vokabelkarten_repository import VokabelkartenRepository
from src.repositories.vokabelbox_repository import (VokabelboxRepository)
from src.classes.vokabelkarte import Vokabelkarte

"""
Im original ist Vokabeltrainer von OrderedCollection abgeleitet und speichert die Vojkabelboxen
Dazu eine instance Variable current Index.
Die Methoden greifen vor allem auf die Liste zu, veraendern den Index.
Ausserdem FileOut- und FileIn-Funktionen 

Funtkion fuer Zeit
(datetime.datetime.now().timestamp()*1000,datetime.datetime.fromisoformat('2024-07-07 02:22:58').timestamp()*1000)
"""
# TODO 1. Implementiere VokabelRepository-Klasse um die ganze speicher und laden auszulagern.
#   Zur Zeit wird nicht in JOSN, sondern vokabelkarten.data und vokabelboxen.data geschrieben.
# TODO: Speicher und Lade den aktuellenIndex und die aktuellenFrageeinheiten in den Vokabelboxen
# TODO: Momentan gibt es noch keine Verwendung der LernUhr.
# TODO import pickle muss verschwinden
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
        # TODO In FactoryKlasse ausgelagern.
        # Funktion wird nur in den Tests benutzt
        [VokabeltrainerModell.addVokabelkarte(karte) for karte in Vokabelkarte.lieferBeispielKarten(anzahl, sprache)]
