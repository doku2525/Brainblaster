from vokabelbox import Vokabelbox
import _pickle as pickle

class VokabelboxRepository:

    def __init__(self, dateiname: str = ''):
        self.dateiname: str = dateiname
        self.vokabelboxen: Vokabelbox = None

    def speichern(self) -> None:     # Alter Name: def speicherVokabelboxInDatei(self):
        pickle.dump(self.vokabelboxen, open(self.dateiname, "wb"))

    def laden(self) -> None:        # Alter Name: def ladeVokabelboxenAusDatei(self):
        self.vokabelboxen = pickle.load(open(self.dateiname, "rb")) if self.vokabelboxen is None else self.vokabelboxen

    def erneut_laden(self) -> None:        # Alter Name: def ladeVokabelboxenAusDatei(self):
        self.vokabelboxen = pickle.load(open(self.dateiname, "rb"))

    def add_box(self, box):     # Alter Name: def addVokabelbox(self, vokBox) -> Vokabeltrainer:
        # TODO
        print(f"\nSelf: {self.__dict__}")
        print(f"\nvokBox: {vokBox.__dict__}")
        if self.existsBoxtitel(vokBox.titel):
            return self
        else:
            self.vokabelboxen = self.vokabelboxen + [vokBox]
            return self

    def remove_box(self, box_id):       # Alter Name def loescheBox(self, titel: str) -> Vokabeltrainer:
        # TODO
        return Vokabeltrainer([box for box in self.vokabelboxen if box.titel != titel], self.aktuellerIndex)

    def rename_box(self, old_name, new_name):  # Alter Name: def renameBox(self, alterTitel: str, neuerTitel: str) -> Vokabeltrainer:
        # TODO
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

    def titelAllerVokabelboxen(self) -> list[str]:
        # TODO
        return [box.titel for box in self.vokabelboxen]

    def existsBoxtitel(self, neuerTitel: str) -> bool:
        # TODO
        print(f"{self.vokabelboxen}")
        return neuerTitel in [box.titel for box in self.vokabelboxen] if self.vokabelboxen is not None else False
