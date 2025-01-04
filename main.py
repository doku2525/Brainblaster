import time
from typing import Callable, cast

from src.classes.configurator import config
from src.classes.eventmanager import EventManager
from src.classes.lernuhr import Lernuhr
from src.classes.vokabeltrainercontroller import VokabeltrainerController
from src.classes.vokabeltrainermodell import VokabeltrainerModell
from src.classes.zustandsbeobachter import Beobachter, ObserverManager
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, JSONDateiformatVokabelkarte
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
from src.views.consoleview import ConsoleView
from src.views.flaskview import FlaskView
from src.zustaende.zustandsmediator import ZustandsMediator
import src.utils.utils_io as u_io


def factory_ViewObserver(view_liste: list[Beobachter]) -> ObserverManager:
    klassen_mediator_dict_fuer_updaten: dict[Beobachter, tuple[Callable, Callable]] = {
        cast(Beobachter, FlaskView): (ZustandsMediator().zustand_to_flaskview_data, ObserverManager().views_updaten),
        cast(Beobachter, ConsoleView): (ZustandsMediator().zustand_to_consoleview_data, ObserverManager().views_updaten)
    }

    if not view_liste:
        return ObserverManager()
    return factory_ViewObserver(
        view_liste[1:]).registriere_mapping(view_liste[0],
                                            *klassen_mediator_dict_fuer_updaten[view_liste[0].__class__])


def main() -> None:
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
    view_observer: ObserverManager = factory_ViewObserver(liste_der_views)
    controller = VokabeltrainerController(modell=modell, uhr=uhr, view_observer=view_observer,
                                          event_manager=event_manager)
    controller.programm_loop()


if __name__ == "__main__":
    main()
