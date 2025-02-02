import time
from typing import Callable, cast, TYPE_CHECKING

# Klassen
from src.classes.configurator import config
from src.classes.eventmanager import EventManager
from src.classes.lernuhr import Lernuhr
from src.classes.programmloop import ProgrammLoop
from src.classes.taskmanager import TaskManager
from src.classes.vokabeltrainercontroller import VokabeltrainerController
from src.classes.vokabeltrainermodell import VokabeltrainerModell
from src.classes.zustandsbeobachter import Beobachter, ObserverManagerFactory
# Kommandos
from src.kommandos.kommandointerpreter import KommandoInterpreter
# Repository
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, JSONDateiformatVokabelkarte
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
# Views
from src.views.consoleview import ConsoleView
from src.views.flaskview import FlaskView
# Zustaende
from src.zustaende.zustandsmediator import ZustandsMediator
from src.zustaende.zustandsfactory import ZustandsFactory
from src.zustaende.workflowmanager import WorkflowManager
# Utils
import src.utils.utils_io as u_io

if TYPE_CHECKING:
    from src.classes.zustandsbeobachter import ObserverManager

"""
Mapping-Dicitionary fuer die ObserverManagerFactory.
    Jeder View-Klasse wird die Konverterfunktion fuer ZustandsDaten->ViewDaten aus dem Zustandsmediator zugewiesen.
    Neue Views muessen hier mit ihrere Mediator-Funktion registriert werden.
    {View-Klasse: ZustandsMediator().zustand_to_???_data}
"""
view_to_mediator_mapping: dict[Beobachter, Callable] = {
    cast(Beobachter, FlaskView): ZustandsMediator().zustand_to_flaskview_data,
    cast(Beobachter, ConsoleView): ZustandsMediator().zustand_to_consoleview_data
}


def main() -> None:
    """
    Initialisiere die Komponenten des Programms, die im Controller benutzt werden:
       - Modell,
       - Uhr,
       - EventManager,
       - Views/Beobachter,
       - ViewObserver(zum updaten der Daten fuer die Views und der Views selbst)
    """
    modell = VokabeltrainerModell(
        vokabelkarten=InMemoryVokabelkartenRepository(dateiname=f"{config.daten_pfad}{config.vokabelkarten_dateiname}",
                                                      verzeichnis='', speicher_methode=JSONDateiformatVokabelkarte),
        vokabelboxen=InMemeoryVokabelboxRepository(dateiname=f"{config.daten_pfad}{config.vokabelboxen_dateiname}",
                                                   speicher_methode=JSONDateiformatVokabelbox))
    uhr = Lernuhr.from_iso_dict(u_io.lese_aus_jsondatei(f"{config.daten_pfad}{config.uhr_dateiname}"))
    event_manager = EventManager()

    flask_html_view = FlaskView(event_manager=event_manager)
    flask_html_view.start_server()
    liste_der_views = [flask_html_view, ConsoleView()]
    view_observer: ObserverManager = ObserverManagerFactory.factory_from_liste(liste_der_views,
                                                                               view_to_mediator_mapping)
    controller = VokabeltrainerController(modell=modell, uhr=uhr, view_observer=view_observer)
    print(f"Stage 1 abgeschlossen!")
    programm_loop = ProgrammLoop(controller=controller,
                                 event_manager=event_manager,
                                 task_manager=TaskManager(),
                                 cmd_interpreter=KommandoInterpreter(),
                                 workflow=WorkflowManager(aktueller_zustand=ZustandsFactory.start_zustand().__class__,
                                                          transitions=ZustandsFactory.transitions()))
    programm_loop.start()

"""
Hier sollte auch die ZustandsFactory initialisiert werden.
Und der StartZustand in den WorkflowManager als aktuellen_zustand und ZustandsFactory.transitions als tranasitions.
Dabei wird eine Instanze von Startzustand im cache. gespeichert. 
So hat StartZustand niemals parrents, weil history immer leer ist.
Wenn in ProgrammLoop der InfoManager fetig gebaut wurde, kann die ZustandsFactory anfangen die in Transition des aktuellen
Zustands gespeicherten Klassen im hintergrund in den Cache zu schreiben. 
"""

if __name__ == "__main__":
    main()
