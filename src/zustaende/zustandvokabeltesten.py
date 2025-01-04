from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Callable, Type, TYPE_CHECKING, cast

from src.zustaende.zustand import ZustandReturnValue, Zustand
from src.classes.antwort import Antwort
if TYPE_CHECKING:
    from src.classes.vokabelkarte import Vokabelkarte
    from src.classes.frageeinheit import Frageeinheit


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
                                          ((aktuelle_karte, neue_karte),))
            if int(cmd_str) < 4:
                """Wenn eine Karte falsch beantwortet wird, die aktuelle Karte wieder ans Ende der output_liste gesetzt.
                Es wird nicht neue_karte benutzt, da neue_karte erst im Controller berechnet wird und zum Wiederholen
                die Veraenderunen in neue_karte keine Rolle spielen."""
                return ZustandReturnValue(
                    replace(self, input_liste=self.input_liste[1:],
                            output_liste=self.output_liste + ([aktuelle_karte] if self.wiederholen else [])),
                    cast(Callable, "update_vokabelkarte_statistik"),
                    ((aktuelle_karte, neue_karte),))

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


@dataclass(frozen=True)
class ZustandVokabelPruefen(ZustandVokabelTesten):
    # TODO Tests
    titel: str = field(default='Zustand Pruefen')
    beschreibung: str = field(default='Zustand Pruefen, fuehrt die Pruefen-Tests aus und verarbeitet Antworten')


@dataclass(frozen=True)
class ZustandVokabelLernen(ZustandVokabelTesten):
    # TODO Tests
    titel: str = field(default='Zustand Lernen')
    beschreibung: str = field(default='Zustand Lernen, fuehrt die Lernen-Tests aus und verarbeitet Antworten')


@dataclass(frozen=True)
class ZustandVokabelNeue(ZustandVokabelTesten):
    # TODO Tests
    titel: str = field(default='Zustand Neue')
    beschreibung: str = field(default='Zustand Neue, fuehrt die Neue-Tests aus und verarbeitet Antworten')
