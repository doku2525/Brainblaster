from __future__ import annotations
from dataclasses import dataclass
import _pickle as pickle
import datetime
import zipfile
from threading import Thread

from libs.repository.vokabelkarten_repository import VokabelkartenRepository
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
# TODO: Speicher und Lade den aktuellenIndex und die aktuellenFrageeinheiten in den Vokabelboxen
# TODO: Momentan gibt es noch keine Verwendung der LernUhr.


# TODO Definiere Klasse als @dataclass
class Vokabeltrainer:

    vokabelkarten = []
    dateiKarten = "./data/vokabelkarten.data"
    dateiKartenBackup = "./data/backups/vokabelkarten."
    dateiKartenJSON = "./data/vokabelkarten.json"

    def __init__(self, vokabelrepository: VokabelkartenRepository, vokabelboxen: list[vokabelbox.Vokabelbox],
                 aktuellerIndex: vokabelbox.Vokabelbox = None):
        self.vokabel_repository = vokabelrepository
        self.vokabelboxen = vokabelboxen
        self.aktuellerIndex = aktuellerIndex
        self.dateiBoxen = "./data/vokabelboxen.data"
        self.dateiBoxenJSON = "./data/vokabelboxen.json"

    def existsBoxtitel(self, neuerTitel: str) -> bool:
        print(f"{self.vokabelboxen}")
        return neuerTitel in [box.titel for box in self.vokabelboxen] if self.vokabelboxen is not None else False

    def titelAllerVokabelboxen(self) -> list[str]:
        return [box.titel for box in self.vokabelboxen]

    def addVokabelbox(self, vokBox) -> Vokabeltrainer:
        if self.existsBoxtitel(vokBox.titel):
            return self
        else:
            return Vokabeltrainer(sorted(self.vokabelboxen + [vokBox]), self.aktuellerIndex)

    def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
        if not self.existsBoxtitel(alterTitel):
            return self
        if self.existsBoxtitel(neuerTitel):
            return self
        result = []
        for i in self.vokabelboxen:
            if i.titel == alterTitel:
                i.titel = neuerTitel
            result.append(i)
        return Vokabeltrainer(sorted(result), self.aktuellerIndex)

    def loescheBox(self, titel: str) -> Vokabeltrainer:
        return Vokabeltrainer([box for box in self.vokabelboxen if box.titel != titel], self.aktuellerIndex)

    def speicherVokabelboxInDatei(self):
        pickle.dump(self.vokabelboxen, open(self.dateiBoxen, "wb"))

    def ladeVokabelboxenAusDatei(self):
        self.vokabelboxen = pickle.load(open(self.dateiBoxen, "rb"))

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
