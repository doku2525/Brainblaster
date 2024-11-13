from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type
from dataclasses import replace

import  json
import _pickle as pickle

from vokabelbox import Vokabelbox
from libs.utils_dataclass import mein_asdict


# TODO Evtl, syncronitaet zwischen den verschiedenen Speichermedien implementieren???
class VokabelboxRepository(ABC):

    @abstractmethod
    def speichern(self) -> None:
        pass

    @abstractmethod
    def laden(self) -> None:
        pass

    @abstractmethod
    def erneut_laden(self) -> None:
        pass

    def add_box(self, box):
        pass

    @abstractmethod
    def remove_box(self, box_id):
        # Alter Name def loescheBox(self, titel: str) -> Vokabeltrainer:
        pass

    @abstractmethod
    def rename_box(self, old_name, new_name):
        # Alter Name: def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
        pass

    @abstractmethod
    def titel_aller_vokabelboxen(self) -> list[str]:
        pass

    @abstractmethod
    def exists_boxtitel(self, neuer_titel: str) -> bool:
        pass


class InMemeoryVokabelboxRepository(VokabelboxRepository):

    def __init__(self, dateiname: str = '', speicher_methode: Type[DateiformatVokabelbox] = None):
        self.dateiname: str = dateiname
        self.speicher_methode: Type[DateiformatVokabelbox] = speicher_methode
        self.vokabelboxen: list[Vokabelbox] = list()

    def speichern(self) -> None:
        # Alter Name: def speicherVokabelboxInDatei(self):
        self.speicher_methode.speichern(self.vokabelboxen, self.dateiname)

    def laden(self) -> bool:
        # Alter Name: def ladeVokabelboxenAusDatei(self):
        if self.vokabelboxen:
            return False
        self.erneut_laden()
        return True

    def erneut_laden(self) -> None:
        # Alter Name: def ladeVokabelboxenAusDatei(self):
        self.vokabelboxen = self.speicher_methode.laden(self.dateiname)

    def add_box(self, box: Vokabelbox) -> None:
        # Alter Name: def addVokabelbox(self, vokBox) -> Vokabeltrainer:
        """
        Fuegt nur Boxen mit neuem Namen hinzu, Boxen mit gleichem Namen werden nicht ersetzt
        :param box:
        """
        if not self.exists_boxtitel(box.titel):
            self.vokabelboxen = self.vokabelboxen + [box]

    def remove_box(self, box_titel: str) -> None:
        # Alter Name def loescheBox(self, titel: str) -> Vokabeltrainer:
        self.vokabelboxen = [box for box in self.vokabelboxen if box.titel != box_titel]

    def rename_box(self, alter_titel: str, neuer_titel: str) -> None:
        # Alter Name: def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
        if not self.exists_boxtitel(alter_titel):
            return None
        if self.exists_boxtitel(neuer_titel):
            return None
        result = [replace(elem, titel=neuer_titel) if elem.titel == alter_titel else elem for elem in self.vokabelboxen]
        self.vokabelboxen = sorted(result)

    def titel_aller_vokabelboxen(self) -> list[str]:
        return [box.titel for box in self.vokabelboxen]

    def exists_boxtitel(self, neuer_titel: str) -> bool:
        return neuer_titel in [box.titel for box in self.vokabelboxen] if self.vokabelboxen is not None else False


class DateiformatVokabelbox(ABC):
    @staticmethod
    @abstractmethod
    def speichern(zu_speichernde_liste: list[Vokabelbox], dateiname: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def laden(dateiname: str) -> list[Vokabelbox]:
        pass


class BINARYDateiformatVokabelbox(DateiformatVokabelbox):

    @staticmethod
    def speichern(zu_speichernde_liste: list[Vokabelbox], dateiname: str) -> None:
        pickle.dump(zu_speichernde_liste, open(dateiname, "wb"))

    @staticmethod
    def laden(dateiname: str) -> list[Vokabelbox]:
        return pickle.load(open(dateiname, "rb"))


class JSONDateiformatVokabelbox(DateiformatVokabelbox):

    @staticmethod
    def speichern(zu_speichernde_liste: list[Vokabelbox], dateiname: str, ensure_ascii: bool = False) -> None:
        with open(dateiname, 'w') as ausgabe_datei:
            json.dump([mein_asdict(box) for box in zu_speichernde_liste], ausgabe_datei,
                      indent=4, ensure_ascii=ensure_ascii)

    @staticmethod
    def laden(dateiname: str) -> list[Vokabelbox]:
        with open(dateiname, 'r') as eingabe_datei:
            data = json.load(eingabe_datei)
        return [Vokabelbox.fromdict(box) for box in data]
