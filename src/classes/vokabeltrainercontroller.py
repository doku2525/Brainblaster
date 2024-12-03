from dataclasses import replace
import datetime
from src.classes.lernuhr import Lernuhr
from src.classes.vokabeltrainermodell import VokabeltrainerModell


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr):
        self.modell = modell
        self.uhr = uhr

    def zeigeVokabelBoxen(self) -> None:
        print("Verfuegbare Vokabelboxen:")
        if self.modell.vokabelboxen.titel_aller_vokabelboxen():
            [print(f"\t{index:2d} {name}")
             for index, name
             in enumerate(self.modell.vokabelboxen.titel_aller_vokabelboxen())]
            print(f"Aktuelle Box: {self.modell.index_aktuelle_box:2d} - {self.modell.aktuelle_box().titel}")
        else:
            print("\t Keine Boxen vorhanden!")

    def zeigeVokabelkartenStats(self) -> None:
        def countLernTypen() -> set:
            return set([karte.lerneinheit.__class__.__name__
                        for karte
                        in self.modell.vokabelkarten.vokabelkarten])
        print(
            f"\tAnzahl der Karten: {len(self.modell.vokabelkarten.vokabelkarten)}\n"
            f"\tAnzahl der LernTypen: {len(countLernTypen())}  {', '.join(countLernTypen())}"
        )

    def programm_loop(self):
        fortsetzen = True
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.modell = replace(self.modell, index_aktuelle_box=80)

        result = self.modell.starte_vokabeltest(lambda karte: karte.lerneinheit.eintrag,
                                                self.uhr.now(Lernuhr.echte_zeit()))
        print(f"Anzahl in Vokabelbox vorhandener Karten: ",
              f"{len(list(self.modell.aktuelle_box().filter_vokabelkarten(self.modell.alle_vokabelkarten())))}")
        print(f"Vokabeln zum pruefen: {len(list(result))}")
        print(f"Aktuelle Frage: {self.modell.aktuelle_box().aktuelle_frage}")
        print(f"Datum der letzten Antwort: ",
              f"{datetime.datetime.fromtimestamp(self.modell.datum_der_letzten_antwort() / 1000).strftime('%F %T.%f')}")

        while fortsetzen:
            print(f"\n\n*** Hauptmenue ***\t\t{self.uhr.as_iso_format(Lernuhr.echte_zeit())[:-7]}",
                  "\n\t(1) Zeige Vokabelboxen",
                  "\n\t(2) Zeige Vokabekartenstats",
                  "\n\t-------------------------\n\t(q) Beende Programm")
            answer = input(f"\n  Was soll ich tun? ")
            if answer.lower() == "q":
                return []
            if answer.lower() == "1":
                self.zeigeVokabelBoxen()
            if answer.lower() == "2":
                self.zeigeVokabelkartenStats()
