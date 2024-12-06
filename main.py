import time
import json

from src.classes.lernuhr import Lernuhr
from src.classes.vokabeltrainercontroller import VokabeltrainerController
from src.classes.vokabeltrainermodell import VokabeltrainerModell
from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository, JSONDateiformatVokabelkarte
from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository, JSONDateiformatVokabelbox
from src.views.flaskview import FlaskView

def main() -> None:
    pass


if __name__ == "__main__":

    modell = VokabeltrainerModell(
        vokabelkarten=InMemoryVokabelkartenRepository(dateiname='daten/data/vokabelkarten.JSON', verzeichnis='',
                                                      speicher_methode=JSONDateiformatVokabelkarte),
        vokabelboxen=InMemeoryVokabelboxRepository(dateiname='daten/data/vokabelboxen.JSON',
                                                   speicher_methode=JSONDateiformatVokabelbox))
    uhr = Lernuhr.lade_aus_jsondatei("daten/data/uhrzeit.json")

#    flask_html_view = FlaskView()
#    flask_html_view.start_server()

    controller = VokabeltrainerController(modell=modell, uhr=uhr)
    controller.programm_loop()
