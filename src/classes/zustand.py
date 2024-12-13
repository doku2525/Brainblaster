from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
import datetime
from typing import Any, Callable, TYPE_CHECKING

from src.classes.lernuhr import Lernuhr, UhrStatus


@dataclass(frozen=True)
class Zustand(ABC):
    data: dict = field(default_factory=dict)
    parent: Zustand | None = field(default=None)
    child: list[Zustand] = field(default_factory=list)
    beschreibung: str = field(default_factory=str)
    titel: str = field(default_factory=str)
    kommandos: list[str] = field(default_factory=list)
    aktuelle_zeit: str = field(default_factory=str)

    def daten_text_konsole(self, presenter: Callable[[dict], str] = None) -> str | None:
        """Erzeuge prettyprint-String der Daten des Zsuatnds fuer die Konsole"""
        return presenter(self.data) if presenter else None

    def info_text_konsole(self) -> str:
        """Erzeuge prettyprint-String mit den moeglichen Aktionen des Zustands fuer die Konsole"""
        return (
            f"{'-'*10}\n" +
            "* Die verfuegbaren Zustaende\n" +
            "".join(
                [f"\t{index} {zustand.titel} : {zustand.beschreibung}\n" for index, zustand in enumerate(self.child)]) +
            f"* Die verfuegbaren Kommandos\n" +
            "".join([f"\t'{command}' + Zahl\n" for command in self.kommandos]))

    def verarbeite_userinput(self, index_child: str) -> tuple[Zustand, Callable, tuple]:
        """Verarbeite den userinput"""
        return (self.child[int(index_child)], lambda: None, tuple()) if index_child else (self, lambda: None, tuple())

    def update_zeit(self, neue_zeit_im_iso_format: str):
        return replace(self, aktuelle_zeit=neue_zeit_im_iso_format)


@dataclass(frozen=True)
class ZustandENDE(Zustand):
    titel: str = field(default='ENDE')
    beschreibung: str = field(default='Beende Programm')

    def info_text_konsole(self) -> str:
        """Erzeuge prettyprint-String mit den moeglichen Aktionen des Zustands fuer die Konsole"""
        return f"Ciao!"


@dataclass(frozen=True)
class ZustandStart(Zustand):
    liste: list[str] = field(default_factory=list)
    aktueller_index: int = 0
    titel: str = 'Zustand 1'
    beschreibung: str = 'Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.'
    child: list[Zustand] = field(default=(ZustandENDE(),))
    kommandos: list[str] = field(default=("+", "-", "="))

    def __post_init__(self):
        object.__setattr__(self,
                           'data',
                           {'liste': self.liste,
                            'aktueller_index': self.aktueller_index,
                            'aktuelle_uhrzeit': self.aktuelle_zeit} if self.liste else {})

    def daten_text_konsole(self, presenter: Callable = None) -> str:
        """Erzeuge prettyprint-String der Daten des Zustands fuer die Konsole"""
        return (f" {self.titel}\n" +
                f"\t {self.beschreibung}\n" +
                ''.join([f"{index:2d} : {boxtitel}\n" for index, boxtitel in enumerate(self.liste)]) +
                f" Aktuelle Uhrzeit: {self.aktuelle_zeit}\n" +
                f" Aktuelle Box: {self.liste[self.aktueller_index]}") if not presenter else presenter(self.data)

    def verarbeite_userinput(self, index_child: str) -> tuple[Zustand, Callable, tuple]:
        """Verarbeite den userinput"""
        if index_child == '':
            return self, lambda: None, tuple()
        if "+" == index_child[0]:
            return (replace(self,
                            aktueller_index=min(len(self.liste)-1, self.aktueller_index + int(index_child[1:]))),
                    lambda: None,
                    tuple())
        if "-" == index_child[0]:
            return (replace(self,
                            aktueller_index=max(0, self.aktueller_index - int(index_child[1:]))),
                    lambda: None,
                    tuple())
        if "=" == index_child[0]:
            kontrollierter_wert = min(len(self.liste)-1, max(0, int(index_child[1:])))
            return replace(self, aktueller_index=kontrollierter_wert), lambda: None, tuple()
        return super().verarbeite_userinput(index_child)


@dataclass(frozen=True)
class ZustandVeraenderLernuhr(Zustand):
    """Vom prinzip her gibt es keine Child-Zustaende, sondern nur den aufrufenden Parentzustand,
    zu dem vonm ZustandStelleUhr aus wieder zurueckgegangen wird."""
    titel: str = 'ZustandStelleUhr'
    beschreibung: str = 'Zustand, zum Stellen der Uhr.'
    child: list[Zustand] = field(default_factory=list)
    kommandos: list[str] = field(default=('s', 'k', 't', 'z'))
    neue_uhr: Lernuhr | None = field(default=None)   # TODO Waere gut wenn JSON der neuen Zeit Uhr
    # TODO Ersetzen Lernuhr durch JSON: Der einzige Aufruf von Lernuhr ist in __post__init__,
    #  um neue_uhrzeit zu definieren. Alle weiteren Vorkommen von self.neue_uhr koennte man auch durch
    #  Operationen auf das JSON-Dictionary ausfuehren und dann im Controller die neue Lernuhr mit Lernuhr.fromdict()
    #  wieder zusammenbauen.

    def __post_init__(self):
        object.__setattr__(self,
                           'data',
                           ({'aktuelle_uhrzeit': self.aktuelle_zeit if self.aktuelle_zeit else ''} |
                            {'neue_uhrzeit': self.neue_uhr.as_iso_format(Lernuhr.echte_zeit())
                             if self.neue_uhr else ''}))

    def daten_text_konsole(self, presenter: Callable = None) -> str:
        """Erzeuge prettyprint-String der Daten des Zustands fuer die Konsole"""
        return (f" {self.titel}\n" +
                f"\t {self.beschreibung}\n" +
                f" Aktuelle Uhrzeit: {self.aktuelle_zeit}\n" +
                f" Neue Uhrzeit: {self.data['neue_uhrzeit']}\n" +
                f"\t Startzeit : {self.neue_uhr.start_zeit if self.neue_uhr is not None else ''}" +
                f"\t Kalkulationszeit : {self.neue_uhr.kalkulations_zeit if self.neue_uhr is not None else ''}" +
                f"\t Tempo : {self.neue_uhr.tempo if self.neue_uhr is not None else ''}" +
                f"\t Modus : {self.neue_uhr.modus if self.neue_uhr is not None else ''}"
                ) if not presenter else presenter(self.data)

    """Zum Stellen der Uhr lauten die Kommandos
        Mit kleinen Buchstaben
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
        vokabeltrainercontroller aufgerufen. return neuerZustand, wechsel_uhr, (self.neue_uhr,)"""

    def verarbeite_userinput(self, index_child: str) -> tuple[Zustand, Callable, tuple]:
        def replace_datum_element_in_uhr_ersetzen(meine_uhr: Lernuhr, attribut: str, neuer_wert: str) -> Lernuhr:
            sekunden = datetime.datetime.fromisoformat(neuer_wert).timestamp()
            return replace(meine_uhr, **{attribut: sekunden})

        def replace_datum_element_in_uhr_zeitspanne(meine_uhr: Lernuhr, attribut: str, zeit_spanne: str) -> Lernuhr:
            einheit = zeit_spanne[-1]
            dauer = int(zeit_spanne[:-1])
            match einheit:
                case 't': time_delta = datetime.timedelta(days=dauer)
                case 'h': time_delta = datetime.timedelta(hours=dauer)
                case 'm': time_delta = datetime.timedelta(minutes=dauer)
                case _: return meine_uhr    # kein definiertes Kommando gefunden.
            return replace(meine_uhr, **{attribut: meine_uhr.__getattribute__(attribut) + time_delta.total_seconds()})

        def select_replace_funktion(meine_uhr: Lernuhr, attribut: str, kommando_str: str) -> Lernuhr:
            if '=' == kommando_str[0]:
                return replace_datum_element_in_uhr_ersetzen(meine_uhr, attribut, kommando_str[1:])
            if kommando_str[0] in ('+', '-'):
                return replace_datum_element_in_uhr_zeitspanne(meine_uhr, attribut, kommando_str)
            return meine_uhr    # Kein definiertes Kommando gefunden

        if index_child == '':
            return self, lambda: None, tuple()
        if "s" == index_child[0]:
            return (replace(self,
                            neue_uhr=select_replace_funktion(self.neue_uhr, 'start_zeit', index_child[1:])),
                    lambda: None,
                    tuple())
        if "k" == index_child[0]:
            return (replace(self,
                            neue_uhr=select_replace_funktion(self.neue_uhr, 'kalkulations_zeit', index_child[1:])),
                    lambda: None,
                    tuple())
        if "t" == index_child[0]:
            uhr = replace(self.neue_uhr, tempo=float(index_child[1:]))
            return replace(self, neue_uhr=uhr), lambda: None, tuple()
        if "z" == index_child[0]:
            if index_child[1] == "e":
                uhr = replace(self.neue_uhr, modus=UhrStatus.ECHT)
            elif index_child[1] == "p":
                uhr = replace(self.neue_uhr, modus=UhrStatus.PAUSE)
            elif index_child[1] == "l":
                uhr = replace(self.neue_uhr, modus=UhrStatus.LAEUFT)
            else:
                return self, lambda: None, tuple()
            return replace(self, neue_uhr=uhr), lambda: None, tuple()
        return self, lambda: None, tuple()
