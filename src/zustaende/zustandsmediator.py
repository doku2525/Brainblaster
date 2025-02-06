from __future__ import annotations
from dataclasses import dataclass, field
from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from src.zustaende.zustand import Zustand


"""
Die Klasse ZustandMediator wandelt die Daten des Zustands in die Daten fuer die verschiedenen Views um.
Jeder Zustand muss eine von ZustandsMediator abgeleitete Klasse haben.
Der Name muss im Attribut zustand der ZustandsMediator-Klassen gespeichert sein, weil darueber die Zuordnung erfolgt,
da beim Aufruf von ZustandsMediator im Attribut klassen ein Mapping der String auf die Konkreten Klassen erfolgt. Dieses
Mapping wird dann von den Funktionen ausgewertet.
"""


@dataclass(frozen=True)
class ZustandsMediator:
    klassen: dict[str, Type] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self,
                           'klassen',
                           {mediator.zustand: mediator
                            for mediator
                            in [subklassen
                                for klasse
                                in self.__class__.__subclasses__()
                                for subklassen
                                in [klasse] + klasse.__subclasses__()]})

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

    # TODO WorkflowManager mit als Argument uebergeben. Ansonsten werden die Optionen/Transitions nicht in
    #       ConcoleView angezeigt.
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
        """Erzeugt den String fuer das Feld 'optionen' (mit anderen Worten 'transition' des WorkflowManagers.
            Vom Prinzip ist es immer die gleiche Vorgehensweise, deshalb hier definiert"""
        # TODO Um die Transitions anzuzeigen, muss hier die aktuelle instanz des WorkflowManagers verarbeitet werden
        # def build_zustand_liste(zustands_liste: list[Zustand], start_index: int = 1) -> list[str]:
        #     """Wandle zustand.parent oder child in Liste aus String um."""
        #     return [f"{index:2d} {der_zustand.titel} : {der_zustand.beschreibung}\n"
        #             for index, der_zustand
        #             in enumerate(zustands_liste, start_index)
        #             if der_zustand is not None]

        def build_cmds_liste(cmds_liste: list[str]) -> list[str]:
            """Wandle die Liste mit den im Zustand definierten Kommandos in einen String um."""
            return [f"'{cmd}' + Zahl\n" for cmd in cmds_liste]
        return ''.join(
#            (build_zustand_liste([workflow.zustands_history], 0) if workflow.zustands_history
#             else ['']) +
#            build_zustand_liste(workflow.transitions[workflow.aktueller_zustand], 1) +
            build_cmds_liste(zustand.kommandos))


@dataclass(frozen=True)
class ZustandMediatorEnde(ZustandsMediator):
    zustand: str = 'ZustandENDE'

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        return {}

    def prepare_consoleview_optionen_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        return f"Ciao!"


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


@dataclass(frozen=True)
class ZustandsMediatorZustandBoxinfo(ZustandsMediator):
    zustand: str = 'ZustandBoxinfo'

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        """Liefer die speziellen Daten fuer Flaskview"""
        return {'info': zustand.info,
                'aktuelle_frageeinheit': zustand.aktuelle_frageeinheit,
                'box_titel': zustand.box_titel} if zustand.info else {}

    def prepare_consoleview_daten_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        """Wird in der Elternklasse zum bauen des data-Dicitonarys verwendet"""
        return (f"Aktuelle Box: {zustand.box_titel}\n" +
                ''.join([f"{frage_einheit} : {infos}\n" for frage_einheit, infos in zustand.info.items()]) +
                f"Aktuelle Frageeinheit: {zustand.aktuelle_frageeinheit}")


@dataclass(frozen=True)
class ZustandsMediatorZustandVokabelTesten(ZustandsMediator):
    zustand: str = 'ZustandVokabelTesten'

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        """Liefer die speziellen Daten fuer Flaskview"""
        if zustand.input_liste:
            return {'frage': zustand.aktuelle_frageeinheit().frage(zustand.input_liste[0].lerneinheit),
                    'antwort': zustand.aktuelle_frageeinheit().antwort(zustand.input_liste[0].lerneinheit),
                    'formatierung': zustand.aktuelle_frageeinheit().titel(),
                    'wiederholung': 'False'}
        if zustand.output_liste:
            return {'frage': zustand.aktuelle_frageeinheit().frage(zustand.output_liste[0].lerneinheit),
                    'antwort': zustand.aktuelle_frageeinheit().antwort(zustand.output_liste[0].lerneinheit),
                    'formatierung': zustand.aktuelle_frageeinheit().titel(),
                    'wiederholung': 'True'}
        return {'frage': 'Fertig',
                'antwort': 'Fertig',
                'formatierung': zustand.aktuelle_frageeinheit().titel(),
                'wiederholung': 'True'}

    def prepare_consoleview_daten_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        """Wird in der Elternklasse zum bauen des data-Dicitonarys verwendet"""
        if zustand.input_liste:
            return (f"Frage: {zustand.aktuelle_frageeinheit().frage(zustand.input_liste[0].lerneinheit)}\n" +
                    f"Antwort: {zustand.aktuelle_frageeinheit().antwort(zustand.input_liste[0].lerneinheit)}")
        if zustand.output_liste:
            return (f"Frage: {zustand.aktuelle_frageeinheit().frage(zustand.output_liste[0].lerneinheit)}\n" +
                    f"Antwort: {zustand.aktuelle_frageeinheit().antwort(zustand.output_liste[0].lerneinheit)}")
        return (f"Frage: Fertig\n" +
                f"Antwort: Fertig")


@dataclass(frozen=True)
class ZustandsMediatorZustandVokabelPruefen(ZustandsMediatorZustandVokabelTesten):
    # TODO Testen
    zustand: str = 'ZustandVokabelPruefen'


@dataclass(frozen=True)
class ZustandsMediatorZustandVokabelLernen(ZustandsMediatorZustandVokabelTesten):
    # TODO Testen
    zustand: str = 'ZustandVokabelLernen'


@dataclass(frozen=True)
class ZustandsMediatorZustandVokabelNeue(ZustandsMediatorZustandVokabelTesten):
    # TODO Testen
    zustand: str = 'ZustandVokabelNeue'


@dataclass(frozen=True)
class ZustandsMediatorZustandZeigeVokabelliste(ZustandsMediator):
    zustand: str = 'ZustandZeigeVokabelliste'

    def zustand_to_flaskview_data(self, zustand: Zustand, zeit_in_ms: int = 0) -> dict:
        """Liefer die speziellen Daten fuer Flaskview"""
        return {'liste': [(element.lerneinheit, element.statistiken) for element in zustand.liste],
                'frageeinheit_titel': zustand.frageeinheit_titel,
                'modus': zustand.modus,
                'box_titel': zustand.vokabelbox_titel} if zustand.liste else {}

    def prepare_consoleview_daten_string(self, zustand: Zustand, zeit_in_ms: int = 0) -> str:
        """Wird in der Elternklasse zum bauen des data-Dicitonarys verwendet"""
        return f"Aktuelle Box: {zustand.vokabelbox_titel}\n"
#        return (f"Aktuelle Box: {zustand.vokabelbox_titel}\n" +
#                ''.join([f"{'--'*10}\n{element.lerneinheit}\n {element.statistiken}\n" for element in zustand.liste]) +
#                f"Aktuelle Frageeinheit: {zustand.aktuelle_frageeinheit}")


@dataclass(frozen=True)
class ZustandsMediatorZustandZeigeVokabellisteKomplett(ZustandsMediatorZustandZeigeVokabelliste):
    zustand: str = 'ZustandZeigeVokabellisteKomplett'


@dataclass(frozen=True)
class ZustandsMediatorZustandZeigeVokabellisteLernen(ZustandsMediatorZustandZeigeVokabelliste):
    zustand: str = 'ZustandZeigeVokabellisteLernen'


@dataclass(frozen=True)
class ZustandsMediatorZustandZeigeVokabellisteNeue(ZustandsMediatorZustandZeigeVokabelliste):
    zustand: str = 'ZustandZeigeVokabellisteNeue'
