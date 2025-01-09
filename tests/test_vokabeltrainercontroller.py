from unittest import TestCase
from unittest.mock import patch

from src.classes.vokabeltrainercontroller import VokabeltrainerController


class test_VokabeltrainerController(TestCase):
    def setUp(self):
        from src.classes.configurator import config
        from src.classes.eventmanager import EventManager
        from src.classes.lernuhr import Lernuhr
        from src.classes.taskmanager import TaskManager, Task
        from src.classes.zustandsbeobachter import ObserverManager
        from src.classes.vokabelbox import Vokabelbox
        from src.classes.vokabelkarte import Vokabelkarte
        from src.classes.vokabeltrainermodell import VokabeltrainerModell
        from src.repositories.vokabelbox_repository import InMemeoryVokabelboxRepository
        from src.repositories.vokabelkarten_repository import InMemoryVokabelkartenRepository
        import src.utils.utils_io as u_io

        self.liste = Vokabelkarte.lieferBeispielKarten(30, 'Chinesisch')
        box = Vokabelbox('Chinesisch', self.liste[0].lerneinheit.__class__, [])
        modell = VokabeltrainerModell(vokabelkarten=InMemoryVokabelkartenRepository(dateiname='', verzeichnis=''),
                                      vokabelboxen=InMemeoryVokabelboxRepository())
        modell.vokabelboxen.vokabelboxen = [box]*3
        modell.vokabelkarten.vokabelkarten = self.liste
        uhr = Lernuhr.from_iso_dict(u_io.lese_aus_jsondatei("__uhr.json"))

    # def test_update_vokabelkarte_statisitk(self):
    #     from src.zustaende.zustandvokabeltesten import ZustandVokabelTesten
    #     from src.classes.frageeinheit import FrageeinheitChinesischBedeutung
    #
    #     zustand = ZustandVokabelTesten(input_liste=self.controller.modell.vokabelkarten.vokabelkarten,
    #                                    aktuelle_frageeinheit=self.controller.modell.aktuelle_box().aktuelle_frage)
    #     result, fun, args = zustand.verarbeite_userinput('a5')
    #     self.controller.update_vokabelkarte_statistik(*args)
    #     self.assertEqual(
    #         5,
    #         self.controller.modell.vokabelkarten.vokabelkarten[0].
    #         lernstats.statistiken[FrageeinheitChinesischBedeutung].antworten[0].antwort)
