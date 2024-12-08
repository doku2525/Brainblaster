from __future__ import annotations
from dataclasses import replace
import datetime
from typing import TYPE_CHECKING

from src.classes.lernuhr import Lernuhr
from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.zustand import Zustand, ZustandStart, ZustandENDE

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr):
        self.modell = modell
        self.uhr = uhr
        self.aktueller_zustand = None

    def programm_loop(self):
        fortsetzen = True
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = ZustandStart(liste=self.modell.vokabelboxen.titel_aller_vokabelboxen(),
                                              aktueller_index=self.modell.index_aktuelle_box)

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            print(self.aktueller_zustand.daten_text_konsole())
            answer = input(f"{self.aktueller_zustand.info_text_konsole()} \n  Was soll ich tun? >")
            self.aktueller_zustand, cmd, args = self.aktueller_zustand.verarbeite_userinput(answer)
            cmd(*args)

        print(self.aktueller_zustand.info_text_konsole())