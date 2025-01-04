from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.zustaende.zustand import ZustandReturnValue, Zustand
from src.classes.displaypattern import DisplayPatternVokabelkarte

if TYPE_CHECKING:
    from src.classes.vokabelkarte import Vokabelkarte


@dataclass(frozen=True)
class ZustandZeigeVokabelliste(Zustand):
    # TODO Tests
    """Zustand zum Anzeigen einer Uebersichtsliste mit den wichtigsten Daten aus Lerneinheit und
        einer Zusammenfassung der Statistiken.
        Sollte mit erzeuge_aus_vokabelliste erzeugt werden, zum Beispiel mit den Listen aus Lerninfo"""
    titel: str = field(default='Zustand Zeige Vokablliste')
    beschreibung: str = field(default='Zustand Zeige Vokabelliste, die wesentlichen Daten der Karten als Liste')
    kommandos: list[str] = field(default=('e',))
    liste: list[DisplayPatternVokabelkarte] = field(default_factory=list)  # Liste von InformationsTypen
    modus: str = field(default_factory=str)
    frageeinheit_titel: str = field(default_factory=str)
    vokabelbox_titel: str = field(default_factory=str)

    @classmethod
    def erzeuge_aus_vokabelliste(cls, vokabelliste: list[Vokabelkarte]) -> cls:
        # TODO Tests
        return cls(liste=[DisplayPatternVokabelkarte.in_vokabel_liste(element) for element in vokabelliste])

    def verarbeite_userinput(self, index_child: str) -> ZustandReturnValue:
        # TODO Tests
        return super().verarbeite_userinput(index_child)


@dataclass(frozen=True)
class ZustandZeigeVokabellisteKomplett(ZustandZeigeVokabelliste):
    modus: str = 'komplett'


@dataclass(frozen=True)
class ZustandZeigeVokabellisteLernen(ZustandZeigeVokabelliste):
    modus: str = 'lernen'


@dataclass(frozen=True)
class ZustandZeigeVokabellisteNeue(ZustandZeigeVokabelliste):
    modus: str = 'neue'
