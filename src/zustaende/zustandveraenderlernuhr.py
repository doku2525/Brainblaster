from __future__ import annotations
from dataclasses import dataclass, field, replace
import datetime
from typing import Callable
from src.classes.lernuhr import Lernuhr, UhrStatus
from src.zustaende.zustand import ZustandReturnValue, Zustand


@dataclass(frozen=True)
class ZustandVeraenderLernuhr(Zustand):
    titel: str = 'ZustandStelleUhr'
    beschreibung: str = 'Zustand, zum Stellen der Uhr.'
    kommandos: list[str] = field(default=('c', 'k', 'p', 'r', 's', 't', 'u', 'z'))
    neue_uhr: Lernuhr | None = field(default=None)

    def parse_user_eingabe(self, cmd_str: list[str]) -> tuple[str, tuple]:
        """
        Befehle zum Aendern der im Zustand gespeicherten neuen Uhr.
        Zum Stellen der Uhr lauten die Kommandos
        Mit kleinen Buchstaben:
                S+Spanne,S-Spanne,S=Datum: zum Festlegen des Startpunktes. Spanne = ZAHL+T|H|M Tage,Stunden,Minuten
                K+Spanne,K-Spanne,K=Datum: Zum Festlegen des Kalkulationspunktes
                T+float: Zum Festlegen des Tempos
                ZP: Pausiere Uhr
                ZL: Laufen Uhr
                ZE: Echte Zeit
            Fuer Datum koennte man dann noch weitere Abstufungen finden wie +-1T, +-1H, +-1M =ISO-Format
        Nach der Eingabe der Kommandos ruft sich der Zustand immer wieder selbst mit den neuen Werten in NeueUhrzeit
        auf. Am Beginn wird fuer neue Uhr die alte Uhr als Ausgangswert genommen. Am Ende kann man dann Abbrechen,
        oder Speichern. Dann wird das Kommando wechsel_uhr(neue_uhr) [Muss noch implemntiert werden] in
        vokabeltrainercontroller aufgerufen. return neuerZustand, wechsel_uhr, (self.neue_uhr,)
        """
        match cmd_str:
            case ['c']: return self.handle_c()
            case ['k', *cmd]: return self.handle_k(cmd)
            case ['p', *cmd]: return self.handle_p(cmd)
            case ['r']: return self.handle_r()
            case ['s', *cmd]: return self.handle_s(cmd)
            case ['t', *cmd]: return self.handle_t(cmd)
            case ['u', 'p', 'd', 'a', 't', 'e']: return 'CmdErsetzeLernuhr', (self.neue_uhr, )
            case ['z', *cmd]: return self.handle_z(cmd)
        return super().parse_user_eingabe(cmd_str)   # Liefert tuple("", tuple())

    # #######################################
    # Handle-Funktion aus match-case-Konstrukt

    def handle_c(self) -> tuple[str, tuple]:
        neuer_zustand = self._replace_neue_uhr(self.neue_uhr.calibrate(self.neue_uhr.echte_zeit()))
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    def handle_k(self, cmd: list[string]) -> tuple[str, tuple]:
        match cmd:
            case ['=', *cmd]: neuer_zustand = self._replace_neue_uhr(self.kalkulation_gleich(cmd))
            case ['+', *cmd]: neuer_zustand = self._replace_neue_uhr(self.kalkulation_plus(cmd))
            case ['-', *cmd]: neuer_zustand = self._replace_neue_uhr(self.kalkulation_minus(cmd))
            case _: neuer_zustand = self
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    def handle_p(self, cmd: list[string]) -> tuple[str, tuple]:
        match cmd:
            case ['b']: neuer_zustand = self._replace_neue_uhr(self.neue_uhr.pausiere(Lernuhr.echte_zeit()))
            case ['e']: neuer_zustand = self._replace_neue_uhr(self.neue_uhr.beende_pause(Lernuhr.echte_zeit()))
            case _: neuer_zustand = self
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    def handle_r(self) -> tuple[str, tuple]:
        neuer_zustand = self._replace_neue_uhr(self.neue_uhr.reset(self.neue_uhr.echte_zeit()))
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    def handle_s(self, cmd: list[string]) -> tuple[str, tuple]:
        match cmd:
            case ['=', *cmd]: neuer_zustand = self._replace_neue_uhr(self.start_gleich(cmd))
            case ['+', *cmd]: neuer_zustand = self._replace_neue_uhr(self.start_plus(cmd))
            case ['-', *cmd]: neuer_zustand = self._replace_neue_uhr(self.start_minus(wert))
            case _: neuer_zustand = self
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    def handle_t(self, cmd: list[str]) -> tuple[str, tuple]:
        neuer_zustand = replace(self, neue_uhr=replace(self.neue_uhr, tempo=float(''.join(cmd))))
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    def handle_z(self, cmd: list[string]) -> tuple[str, tuple]:
        match cmd:
            case ['e']: neuer_zustand = self._replace_neue_uhr(replace(self.neue_uhr, modus=UhrStatus.ECHT))
            case ['l']: neuer_zustand = self._replace_neue_uhr(replace(self.neue_uhr, modus=UhrStatus.LAEUFT))
            case ['p']: neuer_zustand = self._replace_neue_uhr(replace(self.neue_uhr, modus=UhrStatus.PAUSE))
            case _: neuer_zustand = self
        return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)

    # #######################################
    # Hilfsfunktionen, die parse_user_eingabe() aufgerufen werden.

    def _replace_neue_uhr(self, neue_uhr: Lernuhr) -> ZustandVeraenderLernuhr:
        """ Hilfsfunktion fuer match um Redundanz zu verringern"""
        return replace(self, neue_uhr= neue_uhr)

    def kalkulation_gleich(self, neuer_wert: list[str]) -> Lernuhr:
        return replace(self.neue_uhr, kalkulations_zeit=Lernuhr.isostring_to_millis(''.join(neuer_wert)))

    def start_gleich(self, neuer_wert: list[str]) -> Lernuhr:
        return replace(self.neue_uhr, start_zeit=Lernuhr.isostring_to_millis(''.join(neuer_wert)))

    @staticmethod
    def berechne_time_delta(zeit_spanne: str) -> datetime.timedelta:
        """
        Hilfsfunktion fuer die Funktion, die start_zeit und kalaibrierungszeit aus Zeitspannen berechnen
        Z.B.: +1t, -1t, +20h usw. t->Tage, h->Stunden, m->Minuten
        :param zeit_spanne: str
        :return: datetime.timedelta
        """
        einheit = zeit_spanne[-1]
        dauer = int(zeit_spanne[:-1])
        match einheit:
            case 't':
                return datetime.timedelta(days=dauer)
            case 'h':
                return datetime.timedelta(hours=dauer)
            case 'm':
                return datetime.timedelta(minutes=dauer)
            case _:
                return datetime.timedelta(seconds=0)  # kein definiertes Kommando gefunden.

    def kalkulation_plus(self, neuer_wert: list[str]) -> Lernuhr:
        time_delta = self.berechne_time_delta(''.join(neuer_wert))
        return replace(self.neue_uhr,
                       kalkulations_zeit=self.neue_uhr.kalkulations_zeit + time_delta.total_seconds() * 1000)

    def kalkulation_minus(self, neuer_wert: list[str]) -> Lernuhr:
        time_delta = self.berechne_time_delta(''.join(neuer_wert))
        return replace(self.neue_uhr,
                       kalkulations_zeit=self.neue_uhr.kalkulations_zeit - time_delta.total_seconds() * 1000)

    def start_plus(self, neuer_wert: list[str]) -> Lernuhr:
        time_delta = self.berechne_time_delta(''.join(neuer_wert))
        return replace(self.neue_uhr, start_zeit=self.neue_uhr.start_zeit + time_delta.total_seconds() * 1000)

    def start_minus(self, neuer_wert: list[str]) -> Lernuhr:
        time_delta = self.berechne_time_delta(''.join(neuer_wert))
        return replace(self.neue_uhr, start_zeit=self.neue_uhr.start_zeit - time_delta.total_seconds() * 1000)
