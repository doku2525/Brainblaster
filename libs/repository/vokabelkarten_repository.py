from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type

import _pickle as pickle

from vokabelkarte import Vokabelkarte
from frageeinheit import Frageeinheit


class VokabelkartenRepository(ABC):

    @abstractmethod
    def speichern(self) -> None:
        pass

    @abstractmethod
    def laden(self) -> None:
        pass

    @abstractmethod
    def add_karte(self, karte: Vokabelkarte) -> None:
        pass

    @abstractmethod
    def remove_karte(self, karten_id: str) -> Vokabelkarte:
        pass
        # TODO Nach was genau gesucht werden soll weiss ich noch nicht.
        #      Bisher hatte ich noch nicht nach Vokabelkarten gesucht.
        #      Eine Suche in Bezug auf Werte in lerneinheit waeren denkbar.
        #  S.a.: Kommentar zu exists_karte

    @abstractmethod
    def exists_karte(self, karten_id: str) -> bool:
        pass
        # TODO Nach welchen Kriterien Karten als gleich gelten muss in der Klasse Vokabelkarten festgelegt werden
        #  S.a.: Kommentar zu remove_karte()


class InMemoryVokabelkartenRepository(VokabelkartenRepository):

    BACKUP_VERZEICHNIS = "backups/"

    def __init__(self, dateiname: str, verzeichnis: str, speicher_methode: Type[DateiformatVokabelkarte]):
        self.dateiname: str = dateiname
        self.verzeichnis: str = verzeichnis
        self.vokabelkarten: list[Vokabelkarte] = []
        self.speicher_methode: Type[DateiformatVokabelkarte] = speicher_methode
        self.vokabelkarten: list[Vokabelkarte] = []


    def speichern(self) -> None:
        self.speicher_methode.speichern(zu_speichernde_liste=self.vokabelkarten, dateiname=self.dateiname)

    def laden(self) -> bool:
        if not self.vokabelkarten:
            self.vokabelkarten = self.speicher_methode.laden(dateiname=self.dateiname)
            return True
        else:
            return False

    def erneut_laden(self):
        self.vokabelkarten = self.speicher_methode.laden(dateiname=self.dateiname)

    def add_neue_karte(self, vokabelkarte: Vokabelkarte) -> bool:
        if vokabelkarte in self.vokabelkarten:
            return false
        self.vokabelkarten.append(vokabelkarte)

    def remove_karte(self, zu_entfernende_karte: str) -> None:
        self.vokabelkarten = [karte for karte in self.vokabelkarten if karte != zu_entfernende_karte]
        # Koennte auch mit Suchbegriff durchgefuehrt werden

    def exists_karte(self, karten_id: str) -> bool:
        return karten_id in self.vokabelkarten

    def add_neue_antwort(self, vokabelkarte: Vokabelkarte, frageeinheit: Frageeinheit) -> None:
        pass

    def get_by_id(self, id_nummer: int) -> Vokabelkarte:
        pass

    def changed(self) -> None:
        pass

    def update(self, vokabelkarte: Vokabelkarte) -> None:
        pass


class DateiformatVokabelkarte(ABC):
    @staticmethod
    @abstractmethod
    def speichern(zu_speichernde_liste: list[Vokabelbox], dateiname: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def laden(dateiname: str) -> list[Vokabelbox]:
        pass


class BINARYDateiformatVokabelkarte(DateiformatVokabelkarte):

    @staticmethod
    def speichern(zu_speichernde_liste: list[Vokabelbox], dateiname: str) -> None:
        pickle.dump(zu_speichernde_liste, open(dateiname, "wb"))

    @staticmethod
    def laden(dateiname: str) -> list[Vokabelbox]:
        return pickle.load(open(dateiname, "rb"))
