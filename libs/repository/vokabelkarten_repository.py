from vokabelkarte import Vokabelkarte
from frageeinheit import Frageeinheit


class VokabelkartenRepository:

    BACKUP_VERZEICHNIS = "backups/"

    def __init__(self, filename: str, verzeichnis: str):
        self.filename: str = filename
        self.verzeichnis: str = verzeichnis
        self.vokabelkarten: list[Vokabelkarte] = []

    def load_all(self) -> None:
        pass

    def save_all(self):
        pass

    def add_neue_karte(self, vokabelkarte: Vokabelkarte) -> None:
        pass

    def add_neue_antwort(self, vokabelkarte: Vokabelkarte, frageeinheit: Frageeinheit) -> None:
        pass

    def get_by_id(self, id_nummer: int) -> Vokabelkarte:
        pass

    def changed(self) -> None:
        pass

    def update(self, vokabelkarte: Vokabelkarte) -> None:
        pass
