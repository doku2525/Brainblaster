from src.classes.vokabeltrainermodell import VokabeltrainerModell


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell):
        self.modell = modell

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
            print("\n\n*** Hauptmenue ***")
            print("\t Zeige Vokabelboxen (1)")
            print("\t Zeige Vokabekartenstats (2)")
            print("\t Beende Programm (q)")
            answer = input(" Was soll ich tun? ")
            if answer.lower() == "q":
                return []
            if answer.lower() == "1":
                self.zeigeVokabelBoxen()
            if answer.lower() == "2":
                self.zeigeVokabelkartenStats()
