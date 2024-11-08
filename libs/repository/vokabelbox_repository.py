from abc import ABC, abstractmethod
from dataclasses import replace
from vokabelbox import Vokabelbox
import _pickle as pickle


# TODO Als abstrakte Klasse definieren und dann die aktuelle Implementierung in VokabelboxRepositoryBinary verschieben
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
    def remove_box(self, box_id):       # Alter Name def loescheBox(self, titel: str) -> Vokabeltrainer:
        pass

    @abstractmethod
    def rename_box(self, old_name, new_name):  # Alter Name: def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
        pass

    @abstractmethod
    def titel_aller_vokabelboxen(self) -> list[str]:
        pass

    @abstractmethod
    def exists_boxtitel(self, neuer_titel: str) -> bool:
        pass


class BinaryVokabelboxRepository(VokabelboxRepository):

    def __init__(self, dateiname: str = ''):
        self.dateiname: str = dateiname
        self.vokabelboxen: list[Vokabelbox] = list()

    def speichern(self) -> None:     # Alter Name: def speicherVokabelboxInDatei(self):
        pickle.dump(self.vokabelboxen, open(self.dateiname, "wb"))

    def laden(self) -> None:        # Alter Name: def ladeVokabelboxenAusDatei(self):
        self.vokabelboxen = pickle.load(open(self.dateiname, "rb")) if not self.vokabelboxen else self.vokabelboxen

    def erneut_laden(self) -> None:        # Alter Name: def ladeVokabelboxenAusDatei(self):
        self.vokabelboxen = pickle.load(open(self.dateiname, "rb"))

    def add_box(self, box: Vokabelbox) -> None :     # Alter Name: def addVokabelbox(self, vokBox) -> Vokabeltrainer:
        """
        Fuegt nur Boxen mit neuem Namen hinzu, Boxen mit gleichem Namen werden nicht ersetzt
        :param box:
        """
        if not self.exists_boxtitel(box.titel): self.vokabelboxen = self.vokabelboxen + [box]

    def remove_box(self, box_titel: str) -> None:       # Alter Name def loescheBox(self, titel: str) -> Vokabeltrainer:
        self.vokabelboxen = [box for box in self.vokabelboxen if box.titel != box_titel]

    def rename_box(self, alter_titel: str, neuer_titel: str) -> None:  # Alter Name: def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
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
