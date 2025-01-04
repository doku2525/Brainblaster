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
