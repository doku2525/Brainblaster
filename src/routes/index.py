from flask import render_template, request
from werkzeug.wrappers import Request
import datetime
#import main as model
#from vokabeltrainer import Vokabeltrainer
#import frageeinheit
#import lernuhr


# TODO
class IndexRoute:

    def __init__(self, dateiname: str):
        self.trainer = None
        self.dateiname = dateiname
        self.lektion = None
        self.statistikliste = None
    # def __init__(self, trainer: Vokabeltrainer, dateiname: str):
    #     self.trainer = trainer
    #     self.dateiname = dateiname
    #     self.lektion = None
    #     self.statistikliste = self.__ermittleAlleStatistiken()

    def handle_speichern(self, request: Request) -> None:
        command = request.args.get('command', None)
        if command is not None and command == "speichern":
            #self.trainer.speicherVokabelkartenInDatei()
            print(f"Speicher: {command}")

    def handle_lektion(self, request: Request):
        self.lektion = request.args.get('l', None)
        if self.lektion is not None:
            #self.trainer.aktuellerIndex = self.trainer.vokabelboxen[int(self.lektion)]
            print(f"Lektion {self.lektion}")

    def render_template(self) -> str:
        self.handle_speichern(request)
        self.handle_lektion(request)
        title = f"Willkommen zum Vokabeltrainer{ 'Lektion '+self.lektion+'!' if self.lektion else '!' }"
        return render_template(self.dateiname,
                               title="Test Titel",
                               boxen=enumerate([f"Vokabelbox Nr.{x}" for x in range(1,10)]),
                               current=2,
                               statistiken=[{'karten': 100+x} for x in range(1,10)],
                               uhrzeit="12:22:45",
                               currentFrage="Schreiben")
        # return render_template(self.dateiname,
        #                        title=title,
        #                        boxen=enumerate(self.trainer.titelAllerVokabelboxen()),
        #                        current=self.trainer.aktuellerIndex.titel,
        #                        statistiken=self.statistikliste,
        #                        uhrzeit=lernuhr.Lernuhr.lade_uhr_aus_json(model.uhr_datafile).as_iso_format()[:-7],
        #                        currentFrage=self.trainer.aktuellerIndex.aktuelleFrage().titel())

#    def __ermittleAlleStatistiken(self):
#        return [box.sammle_infos(self.trainer.vokabelkarten, lernuhr.Lernuhr.lade_uhr_aus_json(model.uhr_datafile).now())
#                for box in self.trainer.vokabelboxen]
