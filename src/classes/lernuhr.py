from __future__ import annotations
from dataclasses import dataclass
import datetime
from enum import Enum
import jsonpickle
import time

import src.utils.utils_enum as u_enum


class UhrStatus(Enum):
    PAUSE = 1
    LAEUFT = 2
    ECHT = 3


@dataclass(frozen=True)
class Lernuhr:
    kalkulations_zeit: int = 0
    start_zeit: int = 0
    tempo: float = 1.0
    pause: int = 0
    modus: UhrStatus = UhrStatus.ECHT

    @classmethod
    def fromdict(cls, source_dict: dict) -> cls:
        return cls(kalkulations_zeit=source_dict['kalkulations_zeit'],
                   start_zeit=source_dict['start_zeit'],
                   tempo=source_dict['tempo'],
                   pause=source_dict['pause'],
                   modus=u_enum.name_zu_enum(source_dict['modus'], UhrStatus))

    @staticmethod
    def echte_zeit() -> int:
        return int(time.time() * 1000)

    @staticmethod
    def lade_uhr_aus_json(json_dateiname: str) -> Lernuhr:
        with open(json_dateiname, "r") as f:
            return jsonpickle.decode(f.read())

    @staticmethod
    def isostring_to_millis(isostring: String) -> int:
        """Zum Beispiel: isostring_to_millis('2024-04-11 06:00')"""
        return int(datetime.datetime.fromisoformat(isostring).timestamp()*1000)

    def now(self, zeitpunkt_in_ms: int | float = 0) -> int:
        if self.modus == UhrStatus.ECHT:
            return Lernuhr.echte_zeit()
        if self.modus == UhrStatus.LAEUFT:
            return int(self.start_zeit + (zeitpunkt_in_ms - self.kalkulations_zeit) * self.tempo)
        else:
            return int(self.start_zeit + (0 - self.kalkulations_zeit + self.pause) * self.tempo)

    def pausiere(self) -> Lernuhr:
        if self.modus == UhrStatus.PAUSE:
            return Lernuhr(kalkulations_zeit=self.kalkulations_zeit, start_zeit=self.start_zeit,
                           tempo=self.tempo, pause=self.pause, modus=self.modus)
        if self.modus == UhrStatus.ECHT:
            return Lernuhr(self.kalkulations_zeit, self.start_zeit, self.tempo, Lernuhr.echte_zeit(), self.modus)
        else:
            return Lernuhr(self.kalkulations_zeit, self.start_zeit, self.tempo, Lernuhr.echte_zeit(), UhrStatus.PAUSE)

    def beende_pause(self) -> Lernuhr:
        if self.modus == UhrStatus.ECHT:
            return self.Lernuhr(self.kalkulations_zeit, self.start_zeit, self.tempo, Lernuhr.echte_zeit(), self.modus)
        if self.modus == UhrStatus.LAEUFT:
            return self
        else:
            return Lernuhr(self.kalkulations_zeit + Lernuhr.echte_zeit() - self.pause,
                           self.start_zeit, self.tempo, 0, UhrStatus.LAEUFT)

    def reset(self) -> Lernuhr:
        return Lernuhr(Lernuhr.echte_zeit(), self.start_zeit, self.tempo, 0, UhrStatus.LAEUFT)

    def as_iso_format(self) -> str:
        return datetime.datetime.fromtimestamp(self.now() / 1000).strftime('%F %T.%f')

    def as_date(self) -> datetime.date:
        return datetime.datetime.fromtimestamp(self.now() / 1000).date()
