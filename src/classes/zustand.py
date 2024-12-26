from __future__ import annotations
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field, replace, asdict
import datetime
from enum import Enum
from typing import Any, Callable, NamedTuple, Protocol, Type, TYPE_CHECKING, cast

from src.classes.lernuhr import Lernuhr, UhrStatus
from src.classes.vokabelkarte import Vokabelkarte
from src.classes.antwort import Antwort

if TYPE_CHECKING:
    from src.classes.frageeinheit import Frageeinheit


class ZustandReturnValue(NamedTuple):
    zustand: Zustand
    cmd: Callable
    args: tuple


@dataclass(frozen=True)
class Zustand(ABC):
    parent: Zustand | None = field(default=None)
    child: list[Zustand] = field(default_factory=list)
    beschreibung: str = field(default_factory=str)
    titel: str = field(default_factory=str)
    kommandos: list[str] = field(default_factory=list)
    aktuelle_zeit: str = field(default_factory=str)

    def position_zustand_in_child_mit_namen(self, klassen_name: str) -> str:
        """Da 0 fuer die Position parrent reserviert ist, ist result = '' oder '1..n'  """
        return "".join([str(index)
                        for index, zustand
                        in enumerate(self.child, 1) if zustand.__class__.__name__ == klassen_name])

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        """Verarbeite den userinput.
        Der normale userinput, der nicht gefiltert wird ist eine Zahl, die die Position innerhalb
        der Liste aus parrent und child angibt und dann diesen Zustand zurueckgibt.
        0 - Gibt den Zustand in parrent zurueck
        1...n Gibt den x. Zustand aus child zurueck.
        @name Gibt den Zustand mit dem Namen name zurueck.
        Oder """

        # Wandle nicht numerische Kommandos in numerische um
        if index_child and index_child[0] == "@":                              # @ = Suche index nach Namen
            index_child = self.position_zustand_in_child_mit_namen(index_child[1:])

        # Veraerbeite regulaere Kommandos
        if index_child and int(index_child[0]) == 0:                           # 0 = Zurueck zum vorherigen Zustand
            return ZustandReturnValue(self.parent, lambda: None, tuple())
        return ZustandReturnValue(
            zustand=replace(self.child[int(index_child) - 1], parent=self), cmd=lambda: None, args=tuple()
        ) if index_child else ZustandReturnValue(self, lambda: None, tuple())  # Leere String => self als neuer Zustand

    def update_zeit(self, neue_zeit_im_iso_format: str):
        return replace(self, aktuelle_zeit=neue_zeit_im_iso_format)


@dataclass(frozen=True)
class ZustandENDE(Zustand):
    titel: str = field(default='ENDE')
    beschreibung: str = field(default='Beende Programm')


@dataclass(frozen=True)
class ZustandStart(Zustand):
    liste: list[str] = field(default_factory=list)
    aktueller_index: int = 0
    titel: str = 'Zustand 1'
    beschreibung: str = 'Zustand 1, der die aktuelle Box und den Namen der aktuellen Box anzeigt.'
    child: list[Zustand] = field(default=(ZustandENDE(),))
    kommandos: list[str] = field(default=("+", "-", "="))

    def __post_init__(self):
        object.__setattr__(self, 'parent', None)    # Der StartZustand hat kein parent!!!

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        """Verarbeite den userinput"""
        if index_child == '':
            return ZustandReturnValue(self, lambda: None, tuple())
        # Bei Veranderungen rufe die Funktion update_modell_aktueller_index() mit dem neuen Index im Controller auf.
        if "+" == index_child[0]:
            neuer_index = min(len(self.liste)-1, self.aktueller_index + int(index_child[1:]))
            return ZustandReturnValue(replace(self, aktueller_index=neuer_index),
                                      cast(Callable, 'update_modell_aktueller_index'),
                                      (neuer_index,))
        if "-" == index_child[0]:
            neuer_index = max(0, self.aktueller_index - int(index_child[1:]))
            return ZustandReturnValue(replace(self, aktueller_index=neuer_index),
                                      cast(Callable, 'update_modell_aktueller_index'),
                                      (neuer_index,))
        if "=" == index_child[0]:
            neuer_index = min(len(self.liste)-1, max(0, int(index_child[1:])))
            return ZustandReturnValue(replace(self, aktueller_index=neuer_index),
                                      cast(Callable, 'update_modell_aktueller_index'),
                                      (neuer_index,))
        return super().verarbeite_userinput(index_child)


@dataclass(frozen=True)
class ZustandVeraenderLernuhr(Zustand):
    """Vom prinzip her gibt es keine Child-Zustaende, sondern nur den aufrufenden Parentzustand,
    zu dem vonm ZustandStelleUhr aus wieder zurueckgegangen wird."""
    titel: str = 'ZustandStelleUhr'
    beschreibung: str = 'Zustand, zum Stellen der Uhr.'
    child: list[Zustand] = field(default_factory=list)
    kommandos: list[str] = field(default=('s', 'k', 't', 'z', 'p', 'r', 'c'))
    neue_uhr: Lernuhr | None = field(default=None)   # TODO Waere gut wenn JSON der neuen Zeit Uhr
    # TODO Ersetzen Lernuhr durch JSON: Der einzige Aufruf von Lernuhr ist in __post__init__,
    #  um neue_uhrzeit zu definieren. Alle weiteren Vorkommen von self.neue_uhr koennte man auch durch
    #  Operationen auf das JSON-Dictionary ausfuehren und dann im Controller die neue Lernuhr mit Lernuhr.fromdict()
    #  wieder zusammenbauen.
    # TODO Es sollte auch die echte_zeit uebergeben werden. Z.B. fuer Rest usw.

    def __post_init__(self):
        object.__setattr__(self, 'child', [self.parent] if self.parent else [])

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

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        def replace_datum_element_in_uhr_ersetzen(meine_uhr: Lernuhr, attribut: str, neuer_wert: str) -> Lernuhr:
            """Hilfsfunktion fuer select_replace_funktion()"""
            zeit_in_millis = Lernuhr.isostring_to_millis(neuer_wert)
            return replace(meine_uhr, **{attribut: zeit_in_millis})

        def replace_datum_element_in_uhr_zeitspanne(meine_uhr: Lernuhr, attribut: str, zeit_spanne: str) -> Lernuhr:
            """Fuehre die Berechnungen mit Zeitspannen aus. Hilfsfunktion fuer select_replace_funktion()"""
            einheit = zeit_spanne[-1]
            dauer = int(zeit_spanne[:-1])
            match einheit:
                case 't': time_delta = datetime.timedelta(days=dauer)
                case 'h': time_delta = datetime.timedelta(hours=dauer)
                case 'm': time_delta = datetime.timedelta(minutes=dauer)
                case _: return meine_uhr    # kein definiertes Kommando gefunden.
            return replace(meine_uhr,
                           **{attribut: meine_uhr.__getattribute__(attribut) + time_delta.total_seconds() * 1000})

        def select_replace_funktion(meine_uhr: Lernuhr, attribut: str, kommando_str: str) -> Lernuhr:
            """Ersetze das Attribut der Lernuhr mit dem Namen attribut"""
            if '=' == kommando_str[0]:
                return replace_datum_element_in_uhr_ersetzen(meine_uhr, attribut, kommando_str[1:])
            if kommando_str[0] in ('+', '-'):
                return replace_datum_element_in_uhr_zeitspanne(meine_uhr, attribut, kommando_str)
            return meine_uhr    # Kein definiertes Kommando gefunden

        def erzeuge_dict_fuer_replace_command(func: Callable) -> dict:
            """Erzeuge das dictionary, das als kwargs in replace zum erzeugen der neuen Uhr benutzt wird"""
            return {'neue_uhr': func()}

        def handle_zustand(sub_kommando) -> ZustandReturnValue:
            """Behandle die Kommandos fuer z = Zustand/Modus"""
            sub_kommando_handler = {
                "e": replace(self.neue_uhr, modus=UhrStatus.ECHT),
                "p": replace(self.neue_uhr, modus=UhrStatus.PAUSE),
                "l": replace(self.neue_uhr, modus=UhrStatus.LAEUFT)
            }
            if sub_kommando:
                meine_uhr = sub_kommando_handler.get(sub_kommando[0], False)
                return ZustandReturnValue(
                    (replace(self, **erzeuge_dict_fuer_replace_command(lambda: meine_uhr)
                             ) if meine_uhr else self),
                    lambda: None, tuple())
            return ZustandReturnValue(self, lambda: None, tuple())

        def handle_pause(sub_kommando) -> ZustandReturnValue:
            """Behandle die Kommandos fuer p = Pause
            b = Beginn Pause
            e = Ende Pause"""
            sub_kommando_handler = {
                "b": self.neue_uhr.pausiere(Lernuhr.echte_zeit()),
                "e": self.neue_uhr.beende_pause(Lernuhr.echte_zeit())
            }
            if sub_kommando:
                meine_uhr = sub_kommando_handler.get(sub_kommando[0], False)
                return ZustandReturnValue(
                    (replace(self, **erzeuge_dict_fuer_replace_command(lambda: meine_uhr)
                             ) if meine_uhr else self),
                    lambda: None, tuple())
            return ZustandReturnValue(self, lambda: None, tuple())

        # Definiere die Kommandohandler in der ersten Ebene.
        kommando_handlers = {
            's': lambda: ZustandReturnValue(replace(self,
                                                    **erzeuge_dict_fuer_replace_command(
                                                        lambda: select_replace_funktion(
                                                            self.neue_uhr, 'start_zeit', index_child[1:]))
                                                    ), lambda: None, tuple()),
            'k': lambda: ZustandReturnValue(replace(self,
                                                    **erzeuge_dict_fuer_replace_command(
                                                        lambda: select_replace_funktion(
                                                            self.neue_uhr, 'kalkulations_zeit', index_child[1:]))
                                                    ), lambda: None, tuple()),
            't': lambda: ZustandReturnValue(replace(self,
                                                    neue_uhr=replace(self.neue_uhr, tempo=float(index_child[1:]))),
                                            lambda: None, tuple()),
            'z': lambda: handle_zustand(index_child[1]),                # Kommando mit 2. Ebene, suche dort
            'p': lambda: handle_pause(index_child[1]),                  # Kommando mit 2. Ebene, suche dort
            'r': lambda: ZustandReturnValue(replace(self,
                                                    **erzeuge_dict_fuer_replace_command(
                                                        lambda: self.neue_uhr.reset(
                                                            self.neue_uhr.echte_zeit()))), lambda: None, tuple()),
            'c': lambda: ZustandReturnValue(replace(self,
                                                    **erzeuge_dict_fuer_replace_command(
                                                        lambda: self.neue_uhr.calibrate(
                                                            self.neue_uhr.echte_zeit()))), lambda: None, tuple())
        }

        # Leerer String
        if index_child == '':
            return ZustandReturnValue(self, lambda: None, tuple())

        # Suche Kommando in unserem kommando_handler
        neuer_zustand = kommando_handlers.get(index_child[0], None)
        if neuer_zustand is not None:
            return neuer_zustand()

        # Kommando unbekannt und wird an die Superklasse weitergeleitet
        """Da ZustandVeraenderLernuhr auf jeden Fall ein parrent hat, kann mit
        0 -> Zurueck ohne die Veraenderungen in neue_uhr als neue Uhrzeit im Controller zu speichern
        n -> Liefert einen Zustand aus child (beim Erzeugen des aktuellen Zustands wird parrent auch in child kopiert),
                aber der Befehl 'update_uhr' mit dem args neue_uhr wird dem ZustandReturnValue() hinzugefuegt"""
        if (not index_child) or (index_child[0] == "0") or (f"@{self.__class__.__name__}" in index_child):
            return super().verarbeite_userinput(index_child)
        # Fuege dem ZustandReturnValue den Befehl zum Updaten der Uhr hinzu
        return super().verarbeite_userinput(index_child)._replace(**{'cmd': 'update_uhr', 'args': (self.neue_uhr,)})


@dataclass(frozen=True)
class ZustandBoxinfo(Zustand):
    info: dict[str, dict[str, dict[str, str]]] = field(default_factory=dict)
    aktuelle_frageeinheit: str = ''
    box_titel: str = ''
    titel: str = 'Zustand 2'
    beschreibung: str = 'Zustand 2, Zeigt die Boxinfos der aktuellen Box an.'
    child: list[Zustand] = field(default_factory=list)
    kommandos: list[str] = field(default=("+", "-", "="))


@dataclass(frozen=True)
class ZustandVokabelTesten(Zustand):
    """Die aktuelle Vokabelkarte befindet sich an Position -1 der output_liste"""
    input_liste: list[Vokabelkarte] = field(default_factory=list)
    output_liste: list[Vokabelkarte] = field(default_factory=list)
    aktuelle_frageeinheit: Type[Frageeinheit] | None = field(default=None)
    wiederholen: bool = field(default=True)     # Wiederhole solange, bis alle Karten TestModus.FERTIG sind.
    titel: str = field(default='Zustand Testen')
    beschreibung: str = field(default='Zustand Testen, fuehrt die Tests aus und verarbeitet Antworten')
    kommandos: list[str] = field(default=('a', 'e'))

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        """Liefert ein Tupel mit der alten Vokabelkarte und der veraenderten Vokabelkarte.
        Der Controller kann dann im Repository, InfoManager usw. die alte Karte durch die Neue ersetzen"""
        def handle_antwort_bei_wiederholung(cmd_str: str) -> ZustandReturnValue:
            if int(cmd_str) > 3:
                return ZustandReturnValue(replace(self, output_liste=self.output_liste[1:]),
                                          lambda: None, tuple())
            if int(cmd_str) < 4:
                aktuelle_karte = self.output_liste[0]
                return ZustandReturnValue(replace(self, output_liste=self.output_liste[1:] + [aktuelle_karte]),
                                          lambda: None, tuple())

        def handle_antwort(cmd_str: str) -> ZustandReturnValue:
            if not self.input_liste and (not self.output_liste or not self.wiederholen):
                return super().verarbeite_userinput("0")        # Zurueck zu Parrent wenn alles leer oder wiedh-option
            if not self.input_liste and self.output_liste:      # Wenn die input_liste leer ist, dann in Wiederholung
                return handle_antwort_bei_wiederholung(cmd_str)

            aktuelle_karte = self.input_liste[0]
            # Berechnung der neuen Karte als Funk. zurueckgeben, die der Controller mit Frageeinheit und Uhrzeit aufruft
            neue_karte: Callable[[int], Vokabelkarte] = lambda zeit: (
                aktuelle_karte.neue_antwort(
                    frage_einheit=self.aktuelle_frageeinheit, antwort=Antwort(antwort=int(cmd_str), erzeugt=zeit)))
            if int(cmd_str) > 3:
                return ZustandReturnValue(replace(self, input_liste=self.input_liste[1:]),
                                          cast(Callable, "update_vokabelkarte_statistik"),
                                          (aktuelle_karte, neue_karte))
            if int(cmd_str) < 4:
                """Wenn eine Karte falsch beantwortet wird, die aktuelle Karte wieder ans Ende der output_liste gesetzt.
                Es wird nicht neue_karte benutzt, da neue_karte erst im Controller berechnet wird und zum Wiederholen
                die Veraenderunen in neue_karte keine Rolle spielen."""
                return ZustandReturnValue(
                    replace(self, input_liste=self.input_liste[1:],
                            output_liste=self.output_liste + ([aktuelle_karte] if self.wiederholen else [])),
                    cast(Callable, "update_vokabelkarte_statistik"),
                    (aktuelle_karte, neue_karte))

        def handle_edit(cmd_str: str) -> ZustandReturnValue:
            # TODO Noch nicht implementiert
            # TODO Keine Tests implementiert
            return ZustandReturnValue(self, lambda: None, tuple())

        kommando_handlers = {
            'a': lambda: handle_antwort(index_child[1:]),
            'e': lambda: handle_edit(index_child[1:])          # Noch ohne Funktion
        }

        # Leerer String
        if index_child == '':
            return ZustandReturnValue(self, lambda: None, tuple())

        # Suche Kommando in unserem kommando_handler
        neuer_zustand = kommando_handlers.get(index_child[0], None)
        if neuer_zustand is not None:
            return neuer_zustand()

        return super().verarbeite_userinput(index_child)
