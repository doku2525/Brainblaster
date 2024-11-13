from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type

import json
import _pickle as pickle

from vokabelkarte import Vokabelkarte
from frageeinheit import Frageeinheit
from libs.utils_dataclass import mein_asdict


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

    def __init__(self, dateiname: str, verzeichnis: str, vokabelkarten: list[Vokabelkarte] = None,
                 speicher_methode: Type[DateiformatVokabelkarte] = None):
        self.dateiname: str = dateiname
        self.verzeichnis: str = verzeichnis
        self.vokabelkarten: list[Vokabelkarte] = [] if vokabelkarten is None else vokabelkarten
        self.speicher_methode: Type[DateiformatVokabelkarte] = speicher_methode

    def speichern(self) -> None:
        self.speicher_methode.speichern(zu_speichernde_liste=self.vokabelkarten, dateiname=self.dateiname)

    def laden(self) -> bool:
        if self.vokabelkarten:
            return False
        self.erneut_laden()
        return True

    def erneut_laden(self):
        self.vokabelkarten = self.speicher_methode.laden(dateiname=self.dateiname)

    def add_karte(self, vokabelkarte: Vokabelkarte) -> bool:
        if vokabelkarte in self.vokabelkarten:
            return False
        self.vokabelkarten.append(vokabelkarte)
        return True

    def remove_karte(self, zu_entfernende_karte: Vokabelkarte) -> None:
        self.vokabelkarten = [karte for karte in self.vokabelkarten if karte != zu_entfernende_karte]
        # Koennte auch mit Suchbegriff durchgefuehrt werden

    def replace_karte(self, original_karte: Vokabelkarte, neue_karte: Vokabelkarte) -> None:
        """
        Erhaelt die Reihenfolge der Liste. Existiert die neue Karte bereits, findet kein Austausch statt.
        :param original_karte:
        :param neue_karte:
        :return:
        """
        if self.exists_karte(neue_karte):
            return None
        self.vokabelkarten = [karte if karte != original_karte else neue_karte for karte in self.vokabelkarten]

    def exists_karte(self, karte: Vokabelkarte) -> bool:
        return karte in self.vokabelkarten


class DateiformatVokabelkarte(ABC):
    @staticmethod
    @abstractmethod
    def speichern(zu_speichernde_liste: list[Vokabelkarte], dateiname: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def laden(dateiname: str) -> list[Vokabelkarte]:
        pass


class BINARYDateiformatVokabelkarte(DateiformatVokabelkarte):

    @staticmethod
    def speichern(zu_speichernde_liste: list[Vokabelkarte], dateiname: str) -> None:
        pickle.dump(zu_speichernde_liste, open(dateiname, "wb"))

    @staticmethod
    def laden(dateiname: str) -> list[Vokabelkarte]:
        return pickle.load(open(dateiname, "rb"))


class JSONDateiformatVokabelkarte(DateiformatVokabelkarte):

    @staticmethod
    def speichern(zu_speichernde_liste: list[Vokabelkarte], dateiname: str, ensure_ascii: bool = False) -> None:
        """
        Um die Kompatibilitaet zu erhoehen kann ensure_ascii=True gesetzt werden, damit Unicodezeichen in
        Escape-Sequenzen umgewandelt werden.
        :param zu_speichernde_liste: list[Vokabelkarte]
        :param dateiname: str
        :param ensure_ascii: bool = False
        :return: None
        """
        with open(dateiname, 'w') as ausgabe_datei:
            json.dump([mein_asdict(karte) for karte in zu_speichernde_liste], ausgabe_datei,
                      indent=4, ensure_ascii=ensure_ascii)

    @staticmethod
    def laden(dateiname: str) -> list[Vokabelkarte]:
        with open(dateiname, 'r') as eingabe_datei:
            data = json.load(eingabe_datei)
        return [Vokabelkarte.fromdict(karte) for karte in data]
