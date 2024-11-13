from src.classes.vokabeltrainermodell import VokabeltrainerModell

class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell):
        self.modell = modell

    def zeigeVokabelBoxen(self, mein_modell: VokabeltrainerModell) -> None:
        print("Verfuegbare Vokabelboxen:")
        if mein_modell.vokabelboxen.titel_aller_vokabelboxen():
            [print(f"\t {name}")
             for name
             in mein_modell.vokabelboxen.titel_aller_vokabelboxen()]
        else: print("\t Keine Boxen vorhanden!")

    def zeigeVokabelkartenStats(self, mein_modell: VokabeltrainerModell) -> None:
        def countLernTypen() -> int:
            return set([karte.lerneinheit.__class__.__name__
                        for karte
                        in mein_modell.vokabelkarten.vokabelkarten])
        print(
            f"\tAnzahl der Karten: {len(mein_modell.vokabelkarten.vokabelkarten)}\n"
            f"\tAnzahl der LernTypen: {len(countLernTypen())}  {', '.join(countLernTypen())}"
        )

    def programm_loop(self):
        fortsetzen = True
        while fortsetzen:
            print("\n\n*** Hauptmenue ***")
            print("\t Zeige Vokabelboxen (1)")
            print("\t Zeige Vokabekartenstats (2)")
            print("\t Beende Programm (q)")
            answer = input(" Was soll ich tun? ")
            if answer.lower() == "q": return []
            if answer.lower() == "1": self.zeigeVokabelBoxen(self.modell)
            if answer.lower() == "2": self.zeigeVokabelkartenStats(self.modell)
