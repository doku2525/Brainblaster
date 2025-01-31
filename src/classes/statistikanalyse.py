from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.classes.statistik import Statistik


class StatistikAnalyse:

    @staticmethod
    def zu_erwartende_wiederholungen(zeit_punkte: list[int], tage: int, aktuelle_zeit_millis: int) -> str:
        """
        Berechnet den Aufwand für die nächsten `tage` Tage und gibt ihn als String zurück.
        Jede Position im String repräsentiert den Aufwand für einen Tag:
        - result[0] = heute
        - result[1] = morgen
        - result[2] = übermorgen
        - usw.
        Der Aufwand wird als Anzahl der Karten pro Stunde dargestellt, wobei der Wert auf 0-9 begrenzt ist.

        :param zeit_punkte: Liste der Zeitpunkte (Z.B durch eine Konverter-Funktionen box_zu_zeitliste() erzeugt).
        :param tage: Anzahl der Tage, für die der Aufwand berechnet werden soll.
        :param aktuelle_zeit_millis: Aktuelle Zeit in Millisekunden seit der Epoche (Moeglichst von Lehrnuhr.now()).
        :return: String, der den Aufwand für die nächsten Tage darstellt.
        """
        jetzt = datetime.fromtimestamp(aktuelle_zeit_millis / 1000)  # Umrechnung in datetime-Objekt

        """Hilfsfunktion"""
        def berechne_aufwand(tag: int) -> str:
            # Setze die Werte auf Mitternacht bis Mitternacht, ausser fuer den aktuellen Tag
            start_zeit = jetzt if tag == 0 else (jetzt + timedelta(days=tag)).replace(hour=0,
                                                                                      minute=0,
                                                                                      second=0,
                                                                                      microsecond=0)
            ende_zeit = start_zeit.replace(hour=23, minute=59, second=59, microsecond=999)
            stunden_bis_ende = round((ende_zeit - start_zeit).total_seconds() / 3600)
            karten_heute = sum(
                1 for datum in zeit_punkte
                if
                int(start_zeit.timestamp() * 1000) <= datum <= int(ende_zeit.timestamp() * 1000)
            )
            return str(min(9, int(karten_heute / stunden_bis_ende)) if stunden_bis_ende > 0 else 0)

        return "".join(map(berechne_aufwand, range(tage)))

    @staticmethod
    def durchschnittliche_rueckstaendigkeit(statistiken: list[int], aktuelle_zeit_millis: int) -> float:
        """Berechnet den Durchschnittswert der Rückständigkeit der Karten, die wiederholt werden müssen."""
        rueckstaendigkeiten = [aktuelle_zeit_millis - datum for datum in statistiken
                               if datum < aktuelle_zeit_millis]
        if not rueckstaendigkeiten:
            return 0.0

        return sum(rueckstaendigkeiten) / len(rueckstaendigkeiten) / (1000 * 60 * 60 * 24)   # Umrechnung in Tage
