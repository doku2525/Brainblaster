from __future__ import annotations
from dataclasses import replace
import datetime
import time
from typing import TYPE_CHECKING

from src.classes.lernuhr import Lernuhr
from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.zustand import Zustand, ZustandStart, ZustandENDE

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.views.flaskview import FlaskView


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view: FlaskView):
        self.modell = modell
        self.uhr = uhr
        self.aktueller_zustand = None
        self.view = view

    def programm_loop(self):
        fortsetzen = True
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = ZustandStart(liste=self.modell.vokabelboxen.titel_aller_vokabelboxen(),
                                              aktueller_index=self.modell.index_aktuelle_box)
        self.view.data = self.aktueller_zustand.data
        print(self.aktueller_zustand.daten_text_konsole())

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            if self.view.cmd and self.view.cmd[0] == 'c':
                self.aktueller_zustand, cmd, args = self.aktueller_zustand.verarbeite_userinput(self.view.cmd[1:])
                self.view.data = self.aktueller_zustand.data
                self.view.cmd = None
                print(self.aktueller_zustand.daten_text_konsole())
            time.sleep(0.25)

        print(self.aktueller_zustand.info_text_konsole())