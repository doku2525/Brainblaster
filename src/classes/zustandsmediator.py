from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from src.classes.zustand import Zustand


@dataclass(frozen=True)
class ZustandsMediator:
    klassen: dict[str, Type] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self,
                           'klassen',
                           {mediator.zustand: mediator
                            for mediator
                            in [klasse for klasse in self.__class__.__subclasses__()]})

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        """Erstelle das data-Dictionary fuer Flaskview"""
        mediator_objekt = self.klassen[zustand.__class__.__name__]()
        # 'zustand' und 'aktuelle_zeit' sollen in jedem Zustand verfuegbar sein, deshalb hier als dict definiert, das
        #   dann mit dem dictionary der speziellen Mediator-Klasse durch den |-Operanden kombiniert wird.
        return {key: value
                for key, value
                in ({'zustand': mediator_objekt.zustand,
                     'aktuelle_uhrzeit': zustand.aktuelle_zeit} |
                    mediator_objekt.zustand_to_flaskview_data(zustand, zeit_in_ms)).items() if value != ''
                }

    def zustand_to_consoleview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        mediator_objekt = self.klassen[zustand.__class__.__name__]()
        return {key: value
                for key, value
                in {'zustand': mediator_objekt.zustand,
                    'aktuelle_zeit': zustand.aktuelle_zeit,
                    'daten': mediator_objekt.prepare_consoleview_daten_string(zustand, zeit_in_ms),
                    'optionen': mediator_objekt.prepare_consoleview_optionen_string(zustand)
                    }.items() if value != ''}

    def prepare_consoleview_daten_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        """Erzeugt den String fuer das Feld 'daten'.
            Da dieses Feld von dem Zustand abhaengt, sollte es in den erbenden Klassen implementiert werden.
            Da die Funktion zustand_to_consoleview_data leere Felder herausfiltert ist die Funktion hier nur zum
            Vermeiden von Fehlermeldungen und um auch wirklich einen String als Resultat zu liefern"""
        return ''

    def prepare_consoleview_optionen_string(self, zustand: Zustand) -> str:
        """Erzeugt den String fuer das Feld 'optionen'.
            Vom Prinzip ist es immer die gleiche Vorgehensweise, deshalb hier definiert"""
        def build_zustand_liste(zustands_liste: list[Zustand], start_index: int = 1) -> list[str]:
            """Wandle zustand.parent oder child in Liste aus String um."""
            return [f"{index:2d} {der_zustand.titel} : {der_zustand.beschreibung}\n"
                    for index, der_zustand
                    in enumerate(zustands_liste, start_index) if der_zustand is not None]

        def build_cmds_liste(cmds_liste: list[str]) -> list[str]:
            """Wandle die Liste mit den im Zustand definierten Kommandos in einen String um."""
            return [f"'{cmd}' + Zahl\n" for cmd in cmds_liste]

        return ''.join(build_zustand_liste([zustand.parent], 0) +
                       build_zustand_liste(zustand.child, 1) +
                       build_cmds_liste(zustand.kommandos))


@dataclass(frozen=True)
class ZustandMediatorEnde(ZustandsMediator):
    zustand: str = 'ZustandENDE'

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        return {}

    def prepare_consoleview_optionen_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        return f"Ciao! {zustand.parent}"


@dataclass(frozen=True)
class ZustandsMediatorZustandStart(ZustandsMediator):
    zustand: str = 'ZustandStart'

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        """Liefer die speziellen Daten fuer Flaskview"""
        return {'liste': zustand.liste,
                'aktueller_index': zustand.aktueller_index} if zustand.liste else {}

    def prepare_consoleview_daten_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        """Wird in der Elternklasse zum bauen des data-Dicitonarys verwendet"""
        return ((''.join([f"{index:2d} : {titel}\n" for index, titel in enumerate(zustand.liste)])) +
                f"Aktuelle Box: {zustand.liste[zustand.aktueller_index]}")


@dataclass(frozen=True)
class ZustandsMediatorZustandVeraenderLernuhr(ZustandsMediator):
    zustand: str = 'ZustandVeraenderLernuhr'

    @staticmethod
    def __berechne_neue_uhrzeit(zustand: Zustand, zeit_in_ms: int) -> str:
        return zustand.neue_uhr.as_iso_format(zeit_in_ms) if zustand.neue_uhr else ''

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        """Liefer die speziellen Daten fuer Flaskview"""
        return ({'neue_uhrzeit': self.__class__.__berechne_neue_uhrzeit(zustand, zeit_in_ms)} |
                ({'neue_uhr': zustand.neue_uhr.as_iso_dict()} if zustand.neue_uhr else {}))

    def prepare_consoleview_daten_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        return ''.join([
            f"Neue Uhrzeit: {self.__class__.__berechne_neue_uhrzeit(zustand, zeit_in_ms)}\n",
            f"Startzeit : {zustand.neue_uhr.start_zeit if zustand.neue_uhr is not None else ''}\n",
            f"Kalkulationszeit : {zustand.neue_uhr.kalkulations_zeit if zustand.neue_uhr is not None else ''}\n",
            f"Tempo : {zustand.neue_uhr.tempo if zustand.neue_uhr is not None else ''}\n",
            f"Modus : {zustand.neue_uhr.modus if zustand.neue_uhr is not None else ''}\n"])
