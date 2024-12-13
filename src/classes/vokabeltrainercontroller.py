from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import replace
import datetime
import time
from typing import TYPE_CHECKING

from src.classes.lernuhr import Lernuhr
from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.zustand import Zustand, ZustandStart, ZustandENDE, ZustandVeraenderLernuhr

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.views.flaskview import FlaskView


class VokabeltrainerController:

    def __init__(self, modell: VokabeltrainerModell, uhr: Lernuhr, view: FlaskView):
        self.modell = modell
        self.uhr = uhr
        self.aktueller_zustand = None
        self.view = view

    def buildZustandStart(self, zustand: ZustandStart) -> ZustandStart:
        return replace(zustand, **{'liste': self.modell.vokabelboxen.titel_aller_vokabelboxen(),
                                   'aktueller_index': self.modell.index_aktuelle_box,
                                   'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                   'child': (ZustandVeraenderLernuhr(), ZustandENDE())})

    def buildZustandVeraenderLernuhr(self, zustand: ZustandVeraenderLernuhr) -> ZustandVeraenderLernuhr:
        raise NotImplementedError

    def programm_loop(self):
        self.modell.vokabelkarten.laden()
        self.modell.vokabelboxen.laden()
        self.aktueller_zustand = self.buildZustandStart(ZustandStart())
        self.view.data = self.aktueller_zustand.data
        print(self.aktueller_zustand.daten_text_konsole())
        print(self.aktueller_zustand.info_text_konsole())

        while not isinstance(self.aktueller_zustand, ZustandENDE):
            if self.view.cmd and self.view.cmd[0] == 'c':
                self.aktueller_zustand, cmd, args = self.aktueller_zustand.verarbeite_userinput(self.view.cmd[1:])
                print(f"AktuellerZustand {self.aktueller_zustand}")
                self.view.data = self.aktueller_zustand.data
                self.view.cmd = None
                print(self.aktueller_zustand.daten_text_konsole())
                print(self.aktueller_zustand.info_text_konsole())
            self.aktueller_zustand = self.aktueller_zustand.update_zeit(self.uhr.as_iso_format(Lernuhr.echte_zeit()))
            self.view.data = self.aktueller_zustand.data
            time.sleep(0.25)

        print(self.aktueller_zustand.info_text_konsole())
