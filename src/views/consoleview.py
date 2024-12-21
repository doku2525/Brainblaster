from __future__ import annotations
from dataclasses import dataclass, field, replace


@dataclass
class ConsoleView:
    """Consoleview zeigt nur 4 Sachen an:
        - Namen des aktuellen Zustand
        - aktuelles Datum/Zeit der Lernuhr
        - zustandspeziefische Daten des Zustand
        - Optionen, zusammen mit den moeglichen Kommandos"""
    data: dict = field(default_factory=dict)

    def update(self, daten: dict) -> ConsoleView:
        self.data = daten
        return self
        # return replace(self, data=daten)

    def render(self) -> None:
        print(f"{self.render_aktueller_zustand()}\n" +
              f"{self.render_daten()}\n" +
              f"{self.render_aktuelles_datum()}\n" +
              f"{self.render_optionen()}\n"
              )

    def render_aktueller_zustand(self) -> str:
        return f"\n Aktueller Zustand: {self.data['zustand']}"

    def render_aktuelles_datum(self) -> str:
        return f"\n Aktuelles Datum: {self.data['aktuelle_zeit']}"

    def render_daten(self) -> str:
        liste = [f"\t{zeile}" for zeile in self.data['daten'].split("\n")]
        return (f"\n Daten\n" +
                '\n'.join(liste))

    def render_optionen(self) -> str:
        liste_zustand = [f"\t{zeile}" + ("" if zeile.strip()[:1] != '0' else " (Zurueck zu vorherigem Zustand)")
                         for zeile
                         in self.data['optionen'].split("\n") if zeile.strip()[:1].isdigit()]
        liste_commands = [f"\t{zeile}"
                          for zeile in self.data['optionen'].split("\n") if not zeile.strip()[:1].isdigit()]
        return ((f"\n Verfuegbare Zustaende:\n" if len(liste_zustand) > 1 else f"\n Verfuegbarer Zustand:\n") +
                '\n'.join(liste_zustand) +
                (f"\n Verfuegbare Kommandos:\n" if len(liste_commands) > 1 else f"\n Verfuegbares Kommando:\n") +
                '\n'.join(liste_commands)
                )
