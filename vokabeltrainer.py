from __future__ import annotations
from dataclasses import dataclass
import _pickle as pickle
import datetime
import zipfile
from threading import Thread

from libs.repository.vokabelkarten_repository import VokabelkartenRepository
from libs.repository.vokabelbox_repository import BinaryVokabelboxRepository
import vokabelbox
from vokabelkarte import Vokabelkarte

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

# Funktionen nach Aufgabe:
# Vokabelbox:
#    existsBoxtitel(self, neuerTitel: str) -> bool
#    titelAllerVokabelboxen(self) -> list[str]:
#    addVokabelbox(self, vokBox) -> Vokabeltrainer:
#    renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
#    loescheBox(self, titel: str) -> Vokabeltrainer:
#    speicherVokabelboxInDatei(self):
#    ladeVokabelboxenAusDatei(self):
# statische Methoden:
#    neu() -> Vokabeltrainer:
# Klassenmethoden:
#    addBeispiele(cls, anzahl, sprache) -> None:
#    addVokabelkarte(cls, karte) -> None:
#    speicherVokabelkartenInDatei(cls) -> None:
#    ladeVokabelkartenAusDatei(cls) -> None:

# TODO Definiere Klasse als @dataclass
class Vokabeltrainer:

    vokabelkarten = []
    dateiKarten = "./data/vokabelkarten.data"
    dateiKartenBackup = "./data/backups/vokabelkarten."
    dateiKartenJSON = "./data/vokabelkarten.json"

    def __init__(self, vokabelrepository: VokabelkartenRepository, vokabelboxen: list[vokabelbox.Vokabelbox],
                 aktuellerIndex: vokabelbox.Vokabelbox = None):
        self.vokabel_repository = vokabelrepository
        self.vokabelbox_repository = BinaryVokabelboxRepository("./data/vokabelboxen.data")
        self.vokabelboxen = vokabelboxen
        self.aktuellerIndex = aktuellerIndex
        self.dateiBoxen = "./data/vokabelboxen.data"
        self.dateiBoxenJSON = "./data/vokabelboxen.json"

    # def existsBoxtitel(self, neuerTitel: str) -> bool:
    #     # In repo uebertragen
    #     print(f"{self.vokabelboxen}")
    #     return neuerTitel in [box.titel for box in self.vokabelboxen] if self.vokabelboxen is not None else False

    # def titelAllerVokabelboxen(self) -> list[str]:
    #     # In repo uebertragen
    #     return [box.titel for box in self.vokabelboxen]

    # def addVokabelbox(self, vokBox) -> Vokabeltrainer:
    #     # In repo uebertragen
    #     print(f"\nSelf: {self.__dict__}")
    #     print(f"\nvokBox: {vokBox.__dict__}")
    #     if self.existsBoxtitel(vokBox.titel):
    #         return self
    #     else:
    #         self.vokabelboxen = self.vokabelboxen + [vokBox]
    #         return self

    # def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
    #     # In repo uebertragen
    #     if not self.existsBoxtitel(alterTitel):
    #         return self
    #     if self.existsBoxtitel(neuerTitel):
    #         return self
    #     result = []
    #     for i in self.vokabelboxen:
    #         if i.titel == alterTitel:
    #             i.titel = neuerTitel
    #         result.append(i)
    #     return Vokabeltrainer(sorted(result), self.aktuellerIndex)

    # def loescheBox(self, titel: str) -> Vokabeltrainer:
    #     # In repo uebertragen
    #     return Vokabeltrainer([box for box in self.vokabelboxen if box.titel != titel], self.aktuellerIndex)

    # def speicherVokabelboxInDatei(self):
    #     # In repo uebertragen
    #     pickle.dump(self.vokabelboxen, open(self.dateiBoxen, "wb"))

    # def ladeVokabelboxenAusDatei(self):
    #     # In repo uebertragen
    #     self.vokabelboxen = pickle.load(open(self.dateiBoxen, "rb"))

    # def speicherVokabelboxInJSON(self):
    #     data = jsonpickle.encode(self.vokabelboxen)
    #     parsed = json.loads(data)
    #     with open(self.dateiBoxenJSON, "w") as text_file:
    #         print(json.dumps(parsed, indent=4), file=text_file)

    # def ladeVokabelboxenAusJSON(self):
    #     with open(self.dateiBoxenJSON, "r") as f:
    #         self.dateiBoxenJSON = jsonpickle.decode(f.read())

    @staticmethod
    def neu() -> Vokabeltrainer:
        return Vokabeltrainer([], [])

    @classmethod
    def addBeispiele(cls, anzahl, sprache) -> None:
        # TODO In FactoryKlasse ausgelagern.
        # Funktion wird nur in den Tests benutzt
        [Vokabeltrainer.addVokabelkarte(karte) for karte in Vokabelkarte.lieferBeispielKarten(anzahl, sprache)]

    @classmethod
    def addVokabelkarte(cls, karte) -> None:
        # TODO Kann geloescht werden und durch die Methode add_neue_karte() aus dem Repository-Modul ersetzt werden.
        # Hilfsfunktion fuer addBeispiele()
        cls.vokabelkarten += [karte]

    @classmethod
    def speicherVokabelkartenInDatei(cls) -> None:
        # TODO Kann geloescht werden, da Methode in Repository implementiert wurde.
        # TODO Funktion kann wahrscheinlich in main.py oder eine ControllerKlasse ausgelagert werden
        def speicherAlsZip(orginalDatei: str, backupDatei: str):
            zeitstempel = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backupfile = backupDatei + zeitstempel + ".bz"
            with zipfile.ZipFile(backupfile, "w", compression=zipfile.ZIP_BZIP2, compresslevel=9) as f:
                f.write(orginalDatei)
        pickle.dump(trainer.vokabel_repository.vokabelkarten, open(cls.dateiKarten, "wb"))
        speicherThread = Thread(target=speicherAlsZip, args=(cls.dateiKarten, cls.dateiKartenBackup))
        speicherThread.start()

    @classmethod
    def ladeVokabelkartenAusDatei(cls) -> None:
        # TODO Funktion kann wahrscheinlich in main.py oder eine ControllerKlasse ausgelagert werden
        cls.vokabelkarten = pickle.load(open(cls.dateiKarten, "rb"))
