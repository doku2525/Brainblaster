from __future__ import annotations
from dataclasses import dataclass, field, replace
import datetime
from typing import Callable
from src.classes.lernuhr import Lernuhr, UhrStatus
from src.zustaende.zustand import ZustandReturnValue, Zustand


@dataclass(frozen=True)
class ZustandVeraenderLernuhr(Zustand):
    """Vom prinzip her gibt es keine Child-Zustaende, sondern nur den aufrufenden Parentzustand,
    zu dem vonm ZustandStelleUhr aus wieder zurueckgegangen wird."""
    titel: str = 'ZustandStelleUhr'
    beschreibung: str = 'Zustand, zum Stellen der Uhr.'
    kommandos: list[str] = field(default=('s', 'k', 't', 'z', 'p', 'r', 'c'))
    neue_uhr: Lernuhr | None = field(default=None)   # TODO Waere gut wenn JSON der neuen Zeit Uhr
    # TODO Ersetzen Lernuhr durch JSON: Der einzige Aufruf von Lernuhr ist in __post__init__,
    #  um neue_uhrzeit zu definieren. Alle weiteren Vorkommen von self.neue_uhr koennte man auch durch
    #  Operationen auf das JSON-Dictionary ausfuehren und dann im Controller die neue Lernuhr mit Lernuhr.fromdict()
    #  wieder zusammenbauen.
    # TODO Es sollte auch die echte_zeit uebergeben werden. Z.B. fuer Rest usw.

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
            case ['c', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.neue_uhr.calibrate(self.neue_uhr.echte_zeit()))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['k', '=', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.kalkulation_gleich(wert))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['k', '+', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.kalkulation_plus(wert))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['k', '-', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.kalkulation_minus(wert))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['p', 'b']:    # Pause Beginn
                neuer_zustand = self._replace_neue_uhr(self.neue_uhr.pausiere(Lernuhr.echte_zeit()))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['p', 'e']:    # Pause Ende
                neuer_zustand = self._replace_neue_uhr(self.neue_uhr.beende_pause(Lernuhr.echte_zeit()))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['r', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.neue_uhr.reset(self.neue_uhr.echte_zeit()))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['s', '=', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.start_gleich(wert))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['s', '+', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.start_plus(wert))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['s', '-', *wert]:
                neuer_zustand = self._replace_neue_uhr(self.start_minus(wert))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['t', *wert]:
                neuer_zustand = replace(self, neue_uhr=replace(self.neue_uhr, tempo=float(''.join(wert))))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand, )
            case ['u', 'p', 'd', 'a', 't', 'e']:
                return 'CmdErsetzeLernuhr', (self.neue_uhr, )
            case ['z', 'e']:
                neuer_zustand = self._replace_neue_uhr(replace(self.neue_uhr, modus=UhrStatus.ECHT))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['z', 'p']:
                neuer_zustand = self._replace_neue_uhr(replace(self.neue_uhr, modus=UhrStatus.PAUSE))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
            case ['z', 'l']:
                neuer_zustand = self._replace_neue_uhr(replace(self.neue_uhr, modus=UhrStatus.LAEUFT))
                return 'CmdErsetzeAktuellenZustand', (neuer_zustand,)
        return super().parse_user_eingabe(cmd_str)   # Liefert tuple("", tuple())

    # ------------------------------------------
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
        Z.B.: +1t, -1t, +20h usw.
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


    # Kommando unbekannt und wird an die Superklasse weitergeleitet
    """Da ZustandVeraenderLernuhr auf jeden Fall ein parrent hat, kann mit
    0 -> Zurueck ohne die Veraenderungen in neue_uhr als neue Uhrzeit im Controller zu speichern
    n -> Liefert einen Zustand aus child (beim Erzeugen des aktuellen Zustands wird parrent auch in child kopiert),
            aber der Befehl 'update_uhr' mit dem args neue_uhr wird dem ZustandReturnValue() hinzugefuegt"""
    # if (not index_child) or (index_child[0] == "0") or (f"@{self.__class__.__name__}" in index_child):
    #     return super().verarbeite_userinput(index_child)
    # # Fuege dem ZustandReturnValue den Befehl zum Updaten der Uhr hinzu
    # return super().verarbeite_userinput(index_child)._replace(**{'cmd': 'update_uhr', 'args': (self.neue_uhr,)})
