from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Callable, Type, TYPE_CHECKING, cast

from src.classes.filterlistenfactory import FilterlistenFactory
from src.classes.lernuhr import Lernuhr

from src.zustaende.zustand import Zustand, ZustandENDE, ZustandBoxinfo
from src.zustaende.zustandveraenderlernuhr import ZustandVeraenderLernuhr
from src.zustaende.zustandstart import ZustandStart
from src.zustaende.zustandvokabeltesten import (ZustandVokabelTesten, ZustandVokabelPruefen,
                                                ZustandVokabelLernen, ZustandVokabelNeue)
from src.zustaende.zustandzeigevokabelliste import (ZustandZeigeVokabelliste, ZustandZeigeVokabellisteKomplett,
                                                    ZustandZeigeVokabellisteLernen, ZustandZeigeVokabellisteNeue)

if TYPE_CHECKING:
    from src.classes.vokabeltrainermodell import VokabeltrainerModell
    from src.classes.infomanager import InfoManager


"""Fuer jeden neuen Zustand muess:
    0. eine neue ZustandsKlasse in zustand.py definiert werden
    1. eine buildZutandXXX-Funktion definiert werden.
    2. die buildZustandXXX-Funktion in update_zustand registriert werden.
    3. ein Zustandsmediator-Klasse definiert werden.
    falls notwendig:
    4. eine Route in flaskview erstellt werden"""


@dataclass(frozen=True)
class ZustandsFactory:
    modell: VokabeltrainerModell
    uhr: Lernuhr
    info_manager: InfoManager

    @staticmethod
    def zustaende_ohne_update() -> list[Type[Zustand]]:
        return [ZustandVeraenderLernuhr, ZustandVokabelPruefen, ZustandVokabelLernen, ZustandVokabelNeue]

    @staticmethod
    def start_zustand() -> ZustandStart:
        return ZustandStart()

    @staticmethod
    def end_zustand() -> Type[Zustand]:
        return ZustandENDE

    def buildZustandStart(self, zustand: ZustandStart) -> ZustandStart:
        return replace(zustand, **{'liste': self.modell.vokabelboxen.titel_aller_vokabelboxen(),
                                   'aktueller_index': self.modell.index_aktuelle_box,
                                   'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                   'child': (self.buildZustandBoxinfo(ZustandBoxinfo()),
                                             self.buildZustandVeraenderLernuhr(ZustandVeraenderLernuhr()),
                                             ZustandENDE())})

    def buildZustandBoxinfo(self, zustand: ZustandBoxinfo) -> ZustandBoxinfo:
        return replace(zustand, **{'info': self.info_manager.boxen_als_number_dict()[self.modell.index_aktuelle_box],
                                   'aktuelle_frageeinheit': self.modell.aktuelle_box().aktuelle_frage.__name__,
                                   'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                   'box_titel': self.modell.aktuelle_box().titel,
                                   'child': (self.buildZustandVeraenderLernuhr(ZustandVeraenderLernuhr()),
                                             self.buildZustandVokabelPruefen(ZustandVokabelPruefen()),
                                             self.buildZustandVokabelLernen(ZustandVokabelLernen()),
                                             self.buildZustandVokabelNeue(ZustandVokabelNeue()),
                                             self.buildZustandZeigeVokabellisteKomplett(
                                                 ZustandZeigeVokabellisteKomplett()),
                                             self.buildZustandZeigeVokabellisteLernen(
                                                 ZustandZeigeVokabellisteLernen()),
                                             self.buildZustandZeigeVokabellisteNeue(
                                                 ZustandZeigeVokabellisteNeue()))})

    def buildZustandVeraenderLernuhr(self, zustand: ZustandVeraenderLernuhr) -> ZustandVeraenderLernuhr:
        if zustand.aktuelle_zeit == '':
            return replace(zustand, **{'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                                       'neue_uhr': self.uhr})
        return replace(zustand, neue_uhr=self.uhr)

    def buildZustandVokabelTesten(self, zustand: ZustandVokabelTesten, filter_liste: list) -> ZustandVokabelTesten:
        """Basefunktion, die den Zustand zurueckgeliefert.
           Wird von den konkreten build-Funktion fuer pruefen, lernen und neu aufgerufen. (Siehe folgende Funktionen)"""
        return replace(zustand,
                       **{'input_liste': FilterlistenFactory.filter_und_execute(
                                           funktion=None,
                                           filter_liste=filter_liste,
                                           liste_der_vokabeln=self.modell.alle_vokabelkarten()),
                          'aktuelle_frageeinheit': self.modell.aktuelle_box().aktuelle_frage,
                          'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit())})

    def buildZustandVokabelPruefen(self, zustand: ZustandVokabelPruefen) -> ZustandVokabelPruefen:
        filter_liste = FilterlistenFactory.filterliste_vokabeln_pruefen(self.modell.aktuelle_box(),
                                                                        self.uhr.now(Lernuhr.echte_zeit()),
                                                                        20)
        return cast(ZustandVokabelPruefen, self.buildZustandVokabelTesten(zustand, filter_liste))

    def buildZustandVokabelLernen(self, zustand: ZustandVokabelLernen) -> ZustandVokabelLernen:
        filter_liste = FilterlistenFactory.filterliste_vokabeln_lernen(self.modell.aktuelle_box(),
                                                                       self.uhr.now(Lernuhr.echte_zeit()),
                                                                       20)
        return cast(ZustandVokabelLernen, self.buildZustandVokabelTesten(zustand, filter_liste))

    def buildZustandVokabelNeue(self, zustand: ZustandVokabelNeue) -> ZustandVokabelNeue:
        filter_liste = FilterlistenFactory.filterliste_vokabeln_neue(self.modell.aktuelle_box(),
                                                                     self.uhr.now(Lernuhr.echte_zeit()),
                                                                     10)
        return cast(ZustandVokabelNeue, self.buildZustandVokabelTesten(zustand, filter_liste))

    def buildZustandZeigeVokabelliste(self, zustand: ZustandZeigeVokabelliste,
                                      modus: str, liste: list) -> ZustandZeigeVokabelliste:
        return replace(zustand,
                       **{
                           'aktuelle_zeit': self.uhr.as_iso_format(Lernuhr.echte_zeit()),
                           'frageeinheit_titel': self.modell.aktuelle_box().aktuelle_frage().titel(),
                           'vokabelbox_titel': self.modell.aktuelle_box().titel,
                           'modus': modus,
                           'liste': liste
                       })

    def buildZustandZeigeVokabellisteKomplett(
            self, zustand: ZustandZeigeVokabellisteKomplett) -> ZustandZeigeVokabellisteKomplett:
        liste = ZustandZeigeVokabelliste.erzeuge_aus_vokabelliste(
            self.info_manager.boxen[self.modell.index_aktuelle_box].karten).liste
        return cast(ZustandZeigeVokabellisteKomplett,
                    self.buildZustandZeigeVokabelliste(zustand, zustand.modus, liste))

    def buildZustandZeigeVokabellisteLernen(
            self, zustand: ZustandZeigeVokabellisteLernen) -> ZustandZeigeVokabellisteLernen:
        karten = (self.info_manager.boxen[self.modell.index_aktuelle_box].
                  infos[self.modell.aktuelle_box().aktuelle_frage].lernen.insgesamt)
        liste = ZustandZeigeVokabelliste.erzeuge_aus_vokabelliste(karten).liste
        return cast(ZustandZeigeVokabellisteLernen,
                    self.buildZustandZeigeVokabelliste(zustand, zustand.modus, liste))

    def buildZustandZeigeVokabellisteNeue(
            self, zustand: ZustandZeigeVokabellisteNeue) -> ZustandZeigeVokabellisteNeue:
        karten = (self.info_manager.boxen[self.modell.index_aktuelle_box].
                  infos[self.modell.aktuelle_box().aktuelle_frage].neu.aktuell)
        liste = ZustandZeigeVokabelliste.erzeuge_aus_vokabelliste(karten).liste
        return cast(ZustandZeigeVokabellisteNeue,
                    self.buildZustandZeigeVokabelliste(zustand, zustand.modus, liste))

    def update_zustand(self, alter_zustand: Zustand) -> Zustand:
        """Ruft die builder()-Funktionen auf, die die Zustaende mit den aktuellen Werten neu bauen.
        Die Zuordnung der Zustaende zu den buildern wird in der service_liste festgelegt."""
        service_liste: dict[Type[Zustand], Callable] = {
            ZustandVeraenderLernuhr: self.buildZustandVeraenderLernuhr,
            ZustandStart: self.buildZustandStart,
            ZustandBoxinfo: self.buildZustandBoxinfo,
            ZustandVokabelPruefen: self.buildZustandVokabelPruefen,
            ZustandVokabelLernen: self.buildZustandVokabelLernen,
            ZustandVokabelNeue: self.buildZustandVokabelNeue,
            ZustandZeigeVokabellisteKomplett: self.buildZustandZeigeVokabellisteKomplett,
            ZustandZeigeVokabellisteLernen: self.buildZustandZeigeVokabellisteLernen,
            ZustandZeigeVokabellisteNeue: self.buildZustandZeigeVokabellisteNeue
        }
        func = service_liste.get(alter_zustand.__class__, lambda x: x)
        return func(alter_zustand)

    def update_frageeinheit(self, zustand: Zustand):
        return replace(
            zustand,
            child=[replace(alter_zustand, aktuelle_frageeinheit=self.modell.aktuelle_box().aktuelle_frage)
                   if isinstance(alter_zustand, ZustandVokabelTesten) else alter_zustand
                   for alter_zustand
                   in zustand.child])

    def update_with_childs(self, zustand: Zustand):
        return replace(zustand if zustand.__class__ in ZustandsFactory.zustaende_ohne_update()
                       else self.update_zustand(zustand),
                       child=[self.update_zustand(child_zustand)
                              for child_zustand in zustand.child])
