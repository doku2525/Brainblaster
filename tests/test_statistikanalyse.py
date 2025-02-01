from unittest import TestCase
from src.classes.statistikanalyse import StatistikAnalyse


def erzeuge_statistik_liste_zukunft(aktuelle_zeit_in_millis: int = 0) -> list[int]:
    vor_kurzem_millis = aktuelle_zeit_in_millis - 1000  # 1 Sekunde in der Zukunft
    heute_millis = aktuelle_zeit_in_millis + 1000  # 1 Sekunde in der Zukunft
    morgen_millis = aktuelle_zeit_in_millis + 24 * 60 * 60 * 1000  # 1 Tag in der Zukunft
    uebermorgen_millis = aktuelle_zeit_in_millis + 2 * 24 * 60 * 60 * 1000  # 2 Tage in der Zuk
    return ([heute_millis] * (3*24) + [morgen_millis] * (5*24) + [uebermorgen_millis] * (1*24) +
            [vor_kurzem_millis] * (3 * 24))


def erzeuge_statistik_liste_vergangenheit(aktuelle_zeit_in_millis: int = 0) -> list[int]:
    heute_millis = aktuelle_zeit_in_millis - 1000  # 1 Sekunde in der Zukunft
    morgen_millis = aktuelle_zeit_in_millis - 24 * 60 * 60 * 1000  # 1 Tag in der Zukunft
    uebermorgen_millis = aktuelle_zeit_in_millis - 2 * 24 * 60 * 60 * 1000  # 2 Tage in der Zuk
    return [heute_millis] * (3*24) + [morgen_millis] * (5*24) + [uebermorgen_millis] * (1*24)


class test_StatistikAnalyse(TestCase):

    def test_zu_erwartende_wiederholungen(self):
        ein_halber_tag = 12 * 60 * 60 * 1000
        ergebnis = StatistikAnalyse.zu_erwartende_wiederholungen(erzeuge_statistik_liste_zukunft(), 3, 0)
        self.assertEqual('351', ergebnis)
        ergebnis = StatistikAnalyse.zu_erwartende_wiederholungen(erzeuge_statistik_liste_zukunft(), 5, 0)
        self.assertEqual('35100', ergebnis)
        ergebnis = StatistikAnalyse.zu_erwartende_wiederholungen(erzeuge_statistik_liste_zukunft(ein_halber_tag),
                                                                 3, ein_halber_tag)
        self.assertEqual('651', ergebnis)

    def test_durchschnittliche_rueckstaendigkeit(self):
        ein_halber_tag = 12 * 60 * 60 * 1000

        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(
            [10 * ein_halber_tag - ein_halber_tag], 10 * ein_halber_tag)  # ein halber Tag
        self.assertEqual(0.5, ergebnis)

        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(
            [10 * ein_halber_tag - ein_halber_tag]*2, 10 * ein_halber_tag)  # ein 2 x ein halber Tag
        self.assertEqual(0.5, ergebnis)

        # ein halber Tag zureuck und ein halber Tag voraus
        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(
            [10 * ein_halber_tag - ein_halber_tag, 10 * ein_halber_tag + ein_halber_tag],
            10 * ein_halber_tag)
        self.assertEqual(0.5, ergebnis)

        # 1x ein halber Tag zuruck + 1x drei halbe Tag zurueck
        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(
            [10 * ein_halber_tag - ein_halber_tag, 10 * ein_halber_tag - 3 * ein_halber_tag],
            10 * ein_halber_tag)
        self.assertEqual(1, ergebnis)

        # Viele Tage voraus und 72 x 1 Sekunde zurueck. (siehe Liste in erzeuge_statistik_liste_zukunft())
        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(erzeuge_statistik_liste_zukunft(20000), 20000)
        self.assertEqual(1000.0/(24*60*60*1000), ergebnis)  # Koennte durch Rundungsfehler False werden

        # Viele Tage voraus und 72 x 1 Sekunde zurueck mit negativen Werten. (Sollte in Realitaet nicht vorkommen)
        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(erzeuge_statistik_liste_zukunft(0), 0)
        self.assertEqual(1000.0/(24*60*60*1000), ergebnis)  # Koennte durch Rundungsfehler False werden

        # 3*24 1s, 5*24 einTag+1sekunde, 1*24 zweiTage+1sekunde (siehe erzeuge_statistik_liste_vergangenheit())
        ergebnis = StatistikAnalyse.durchschnittliche_rueckstaendigkeit(
            erzeuge_statistik_liste_vergangenheit(10 * ein_halber_tag), 10 * ein_halber_tag)
        ein_tag_in_sek = 24*60*60
        calculated_value = (3 * 24 + 5 * 24 * ein_tag_in_sek + 24 * 2 * ein_tag_in_sek) / (72+120+24)
        self.assertEqual(calculated_value/ein_tag_in_sek, ergebnis)  # Koennte durch Rundungsfehler False werden
