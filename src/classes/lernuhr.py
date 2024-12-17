from __future__ import annotations

import json
from dataclasses import dataclass, replace
import datetime
from enum import Enum
import jsonpickle
import time

import src.utils.utils_enum as u_enum
import src.utils.utils_dataclass as u_dataclass


class UhrStatus(Enum):
    PAUSE = 1
    LAEUFT = 2
    ECHT = 3


"""
Die Lernuhr rechnet intern in Millisekunden. Deshalb sollten keine externen Funktionen aus dem datetime-Modul benutzt
werden. Hier in Lernuhr sind Funktionen echte_zeit(), isostring_to_millis() und as_isostring() definiert.
Der Standardfall fuer Lernuhr waere eine Pause beim Testen usw. wieder aufzuholen.
    Problem: Seit 10 Tagen das Programm nicht mehr benutzt und jetzt ist ein riesen Zahl an zu testenden Vokabeln.
    Loesung: start_zeit=jetzt-10Tage und kalkulations_zeit=jetzt und tempo=2.0
    Ergebniss: Jetzt ist 1 Tag auf der normalen Uhr == 2 Tage auf der Lernuhr. Nach 10 Tagen ist der Rueckstand dann
                wieder aufgeholt.
    siehe auch: test_now_zehn_tage_testfall() im Unittest
"""


@dataclass(frozen=True)
class Lernuhr:
    """Alle Zeitangaben sind in Millisekunden. Bei Werten in Sekunden wird das expliziet angegeben!"""
    kalkulations_zeit: int = 0
    start_zeit: int = 0
    tempo: float = 1.0
    pause: int = 0
    modus: UhrStatus = UhrStatus.ECHT

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(kalkulations_zeit=source_dict['kalkulations_zeit'],
                   start_zeit=source_dict['start_zeit'],
                   tempo=float(source_dict['tempo']),
                   pause=source_dict['pause'],
                   modus=u_enum.name_zu_enum(source_dict['modus'], UhrStatus))

    @staticmethod
    def echte_zeit() -> int:
        """Liefert die reale Zeit vom System in Millisekunden.
        Diese Funktion ist die Schnittstelle zum Betriebssystem"""
        return int(time.time() * 1000)

    def speicher_in_jsondatei(self, json_dateiname: str) -> None:
        dic = self.as_iso_dict()
        with open(json_dateiname, "w") as file:
            json.dump(dic, file, indent=4, ensure_ascii=True)

    @staticmethod
    def lade_aus_jsondatei(json_dateiname: str) -> Lernuhr:
        with open(json_dateiname, "r") as file:
            data = json.load(file)
        return Lernuhr.from_iso_dict(data)
        # result = Lernuhr.fromdict(data)
        # result = replace(result, kalkulations_zeit=Lernuhr.isostring_to_millis(result.kalkulations_zeit))
        # return replace(result, start_zeit=Lernuhr.isostring_to_millis(result.start_zeit))

    @staticmethod
    def isostring_to_millis(isostring: str) -> int:
        """Zum Beispiel: isostring_to_millis('2024-04-11 06:00')"""
        return int(datetime.datetime.fromisoformat(isostring).timestamp() * 1000)

    def now(self, zeitpunkt_in_ms: int | float = 0) -> int:
        """Als Normalfall sollte die aktuelle Zeit Lernuhr.echte_zeit() uebergeben werden"""
        if self.modus == UhrStatus.ECHT:
            return Lernuhr.echte_zeit()
        if self.modus == UhrStatus.LAEUFT:
            return int(self.start_zeit + (zeitpunkt_in_ms - self.kalkulations_zeit) * self.tempo)
        else:
            return int(self.start_zeit + (0 - self.kalkulations_zeit + self.pause) * self.tempo)

    def pausiere(self, pausen_beginn_in_ms: int = 0) -> Lernuhr:
        """Als Normalfall sollte die aktuelle Zeit Lernuhr.echte_zeit() uebergeben werden"""
        if self.modus == UhrStatus.PAUSE:
            return Lernuhr(kalkulations_zeit=self.kalkulations_zeit, start_zeit=self.start_zeit,
                           tempo=self.tempo, pause=self.pause, modus=self.modus)
        if self.modus == UhrStatus.ECHT:
            return Lernuhr(self.kalkulations_zeit, self.start_zeit, self.tempo, pausen_beginn_in_ms, self.modus)
        else:
            return Lernuhr(self.kalkulations_zeit, self.start_zeit, self.tempo, pausen_beginn_in_ms, UhrStatus.PAUSE)

    def beende_pause(self, pausen_ende_in_ms: int = 0) -> Lernuhr:
        """Als Normalfall sollte die aktuelle Zeit Lernuhr.echte_zeit() uebergeben werden"""
        if self.modus == UhrStatus.ECHT:
            return Lernuhr(self.kalkulations_zeit, self.start_zeit, self.tempo, pausen_ende_in_ms, self.modus)
        if self.modus == UhrStatus.LAEUFT:
            return self
        else:
            return Lernuhr(self.kalkulations_zeit + pausen_ende_in_ms - self.pause,
                           self.start_zeit, self.tempo, 0, UhrStatus.LAEUFT)

    def reset(self, neue_kalkulations_zeit_in_ms: int = 0) -> Lernuhr:
        """
        Als Normalfall sollte die aktuelle Zeit Lernuhr.echte_zeit() uebergeben werden

        Sollte vor groesseren Tempowechseln ausgefuehrt werden.
            Wenn man das Tempo aendert und der Unterschied von kalkulations_zeit und aktueller_zeit zu gross ist,
            dann koennen relativ grosse Zeitspruenge entstehen. In dem Fall sollte man ein reset(aktuelle_zeit)
            durchfuehren.
            Zum Beispiel:
                100 Tage Unterschied und Aenderung um 0.1 ist ein Sprung von 10 Tagen.
                1 Tag Unterschied und eine Aenderung um 0.1 ist ein Sprung von 144 Minuten"""
        return Lernuhr(neue_kalkulations_zeit_in_ms, self.start_zeit, self.tempo, 0, UhrStatus.LAEUFT)

    def calibrate(self, zeitpunkt_in_ms: int | float = 0) -> Lernuhr:
        """
        Setzt die Startzeit auf die aktuelle Uhrzeit der Lernuhr. Zusammen mit einem Reset hat man dann wieder eine
        frische Uhr, mit wirksamen Tempoveraenderungen.
        :param zeitpunkt_in_ms:
        :return:
        """
        return Lernuhr(self.kalkulations_zeit, self.now(zeitpunkt_in_ms), self.tempo, self.pause, self.modus)

    def as_iso_format(self, zeit_in_ms: int | float = 0) -> str:
        """Als Normalfall sollte die aktuelle Zeit Lernuhr.echte_zeit() uebergeben werden"""
        return datetime.datetime.fromtimestamp(self.now(zeit_in_ms) / 1000).strftime('%F %T.%f')

    def as_date(self, zeit_in_ms: int | float = 0) -> datetime.date:
        """Als Normalfall sollte die aktuelle Zeit Lernuhr.echte_zeit() uebergeben werden"""
        return datetime.datetime.fromtimestamp(self.now(zeit_in_ms) / 1000).date()

    def as_iso_dict(self) -> dict:
        """Wandle die Zeiteingaben von Millisekunden ins ISO-Format um"""
        dic = u_dataclass.mein_asdict(self)
        dic["kalkulations_zeit"] = datetime.datetime.fromtimestamp(self.kalkulations_zeit / 1000).strftime('%F %T.%f')
        dic["start_zeit"] = datetime.datetime.fromtimestamp(self.start_zeit / 1000).strftime('%F %T.%f')
        return dic

    @staticmethod
    def from_iso_dict(dic_mit_iso: dict) -> Lernuhr:
        """Wandle ein Dictionary mit Zeitangaben im ISO-Fromat in eine Lernuhr um."""
        result = Lernuhr.fromdict(dic_mit_iso)
        result = replace(result, kalkulations_zeit=Lernuhr.isostring_to_millis(result.kalkulations_zeit))
        return replace(result, start_zeit=Lernuhr.isostring_to_millis(result.start_zeit))
