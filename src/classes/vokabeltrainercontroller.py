from src.classes.lernuhr import Lernuhr
from src.classes.vokabeltrainermodell import VokabeltrainerModell


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr):
        self.modell = modell
        self.uhr = uhr

    def zeigeVokabelBoxen(self) -> None:
        print("Verfuegbare Vokabelboxen:")
        if self.modell.vokabelboxen.titel_aller_vokabelboxen():
            [print(f"\t {name}")
             for name
             in self.modell.vokabelboxen.titel_aller_vokabelboxen()]
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
