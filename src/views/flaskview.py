from dataclasses import asdict
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_weasyprint import HTML, render_pdf
import inspect
from threading import Thread
import time
from typing import Any

from src.classes.eventmanager import EventManager, EventTyp


# Dictionary mit den Zustaenden, die eigene Routen haben.
# TODO Wird noch nicht benutzt
zustand_zu_route = {
    'ZustandStart': '/index',
    'ZustandVeraenderLernuhr': '/editor_lernuhr'
}

# Dictionary mit den Routen, die eigene Zustaende haben.
# TODO Wird noch nicht benutzt
route_zu_zustand = {value: key for key, value in zustand_zu_route.items()}

# TODO Wird noch nicht benutzt
argumente_zu_kommando = {
    'lernuhr': {'ohne_speichern': lambda route: f"c0",
                'mit_speichern': lambda route: f"@{route}"}
}


def request_to_route(adresse: str, default: str = 'index') -> str:
    """Ermittelt den String fuer """
    result = adresse.split('/')[-1] if adresse else default
    return result if result else default


class FlaskView:

    def __init__(self, event_manager: EventManager) -> None:

        self.app = Flask(__name__, template_folder='templates')

#        self.routes = FlaskRoutes(self.app)
#        self.routes.register_routes()

        self.data = {}
        self.event_manager = event_manager
        self.cmd = False
        self.warte_zeit = 0.25      # siehe Funktion warte_auf_update()

        @self.app.route('/')
        def root():
            return redirect(url_for('index'))

        @self.app.route('/index')
        def index():
            # TODO verkuerzen durch Benutzung der Dictionarys oben
            command = request.args.get('lernuhr', False)
            if command:
                if command == 'ohne_speichern':
                    self.setze_cmd_warte_auf_update('c0', self.warte_zeit)
                elif command == 'mit_speichern':
                    self.setze_cmd_warte_auf_update('c@ZustandStart', self.warte_zeit)
                return redirect(url_for('index'))           # sorgt dafuer, dass args nicht in url angezeigt werden
            return render_template('index.html',
                                   data=enumerate(self.data['liste']),
                                   aktueller_index=self.data['aktueller_index'],
                                   aktuelle_uhrzeit=self.data['aktuelle_uhrzeit'][:-7])

        @self.app.route('/editor_lernuhr')
        def editor_lernuhr():
            self.setze_cmd_warte_auf_update('c@ZustandVeraenderLernuhr', self.warte_zeit)
            return render_template('editor_lernuhr.html',
                                   aktuelle_uhrzeit=self.data['aktuelle_uhrzeit'][:-7],
                                   neue_uhrzeit=self.data['neue_uhrzeit'][:-7],
                                   start_zeit=self.data['neue_uhr']['start_zeit'],
                                   kalkulations_zeit=self.data['neue_uhr']['kalkulations_zeit'],
                                   tempo_wert=int(self.data['neue_uhr']['tempo'] // 1),
                                   tempo_kommastellen=round(self.data['neue_uhr']['tempo'] % 1, 3),
                                   modus=self.data['neue_uhr']['modus'],
                                   neue_uhr=jsonify(self.data['neue_uhr']))

        @self.app.route('/boxinfo')
        def boxinfo():
            self.setze_cmd_warte_auf_update('c@ZustandBoxinfo', self.warte_zeit+1)
            return render_template('boxinfo.html',
                                   aktuelle_uhrzeit=self.data['aktuelle_uhrzeit'][:-7],
                                   info=self.data['info'],
                                   aktuelle_frageeinheit=self.data['aktuelle_frageeinheit'],
                                   box_titel=self.data['box_titel']
                                   )

        @self.app.route('/karten_testen')
        def karten_testen():
            """Fuer die Zustaende pruefen, lernen und neue wird das gleiche Template benutzt.
            Die Routen fuer pruefen, lernen und neue setzen nur den Zustand und leiten dann zu dieser Route weiter."""
            command = request.args.get('zurueck', False)
            if command:
                self.setze_cmd_warte_auf_update('c0', self.warte_zeit)
                return redirect(url_for('boxinfo'))

            self.setze_cmd_warte_auf_update(f"c@{self.data['zustand']}", self.warte_zeit)
            return render_template('karten_testen.html',
                                   frage=self.data['frage'],
                                   antwort=self.data['antwort'],
                                   formatierung=self.data['formatierung'],
                                   zustand=self.data['zustand'])

        @self.app.route('/karten_pruefen')
        def karten_pruefen():
            """Fange das Kommando zum Aendern der Frageeinheit ab, setze dann den Zustand auf Pruefen und leite weiter
            zur Route /karten_testen"""
            command = request.args.get('fe', False)
            if command:
                self.setze_cmd_warte_auf_update(f"c={command}", self.warte_zeit)
            self.setze_cmd_warte_auf_update(f"c@ZustandVokabelPruefen", self.warte_zeit)
            return redirect(url_for('karten_testen'))

        @self.app.route('/karten_lernen')
        def karten_lernen():
            """Fange das Kommando zum Aendern der Frageeinheit ab, setze dann den Zustand auf Lernen und leite weiter
            zur Route /karten_testen"""
            command = request.args.get('fe', False)
            if command:
                self.setze_cmd_warte_auf_update(f"c={command}", self.warte_zeit)
            self.setze_cmd_warte_auf_update(f"c@ZustandVokabelLernen", self.warte_zeit)
            return redirect(url_for('karten_testen'))

        @self.app.route('/karten_neue')
        def karten_neue():
            """Fange das Kommando zum Aendern der Frageeinheit ab, setze dann den Zustand auf Neue und leite weiter
            zur Route /karten_testen"""
            command = request.args.get('fe', False)
            if command:
                self.setze_cmd_warte_auf_update(f"c={command}", self.warte_zeit)
            self.setze_cmd_warte_auf_update(f"c@ZustandVokabelNeue", self.warte_zeit)
            return redirect(url_for('karten_testen'))

        @self.app.route('/zeige_vokabelliste')
        def zeige_vokabelliste():
            """Bei pdf-Option wird return render_pdf(HTML(string=html)) aufgerufen."""
            command = request.args.get('zurueck', False)
            pdf = request.args.get('pdf', False)
            if command:
                self.setze_cmd_warte_auf_update('c0', self.warte_zeit)
                return redirect(url_for('boxinfo'))

            self.setze_cmd_warte_auf_update(f"c@ZustandZeigeVokabelliste", self.warte_zeit)
            html = render_template('zeigevokabelliste.html',
                                   titel=self.data['box_titel'],
                                   untertitel=f"{self.data.get('modus','')}:{self.data.get('frageeinheit_titel','')}",
                                   karten=self.data['liste'])  # karten=[karte.lerneinheit for karte in kartenListe])
            if pdf:
                return render_pdf(HTML(string=html))
            return html

        @self.app.route('/zeige_vokabelliste_komplett')
        def zeige_vokabelliste_komplett():
            command = request.args.get('fe', False)
            pdf = request.args.get('pdf', False)
            if command:
                self.setze_cmd_warte_auf_update(f"c={command}", self.warte_zeit)
            self.setze_cmd_warte_auf_update(f"c@ZustandZeigeVokabellisteKomplett", self.warte_zeit)
            return redirect(
                url_for('zeige_vokabelliste', pdf=True)) if pdf else redirect(
                url_for('zeige_vokabelliste'))

        @self.app.route('/zeige_vokabelliste_lernen')
        def zeige_vokabelliste_lernen():
            command = request.args.get('fe', False)
            pdf = request.args.get('pdf', False)
            if command:
                self.setze_cmd_warte_auf_update(f"c={command}", self.warte_zeit)
            self.setze_cmd_warte_auf_update(f"c@ZustandZeigeVokabellisteLernen", self.warte_zeit)
            return redirect(
                url_for('zeige_vokabelliste', pdf=True)) if pdf else redirect(
                url_for('zeige_vokabelliste'))

        @self.app.route('/zeige_vokabelliste_neue')
        def zeige_vokabelliste_neue():
            command = request.args.get('fe', False)
            pdf = request.args.get('pdf', False)
            if command:
                self.setze_cmd_warte_auf_update(f"c={command}", self.warte_zeit)
            self.setze_cmd_warte_auf_update(f"c@ZustandZeigeVokabellisteNeue", self.warte_zeit)
            return redirect(
                url_for('zeige_vokabelliste', pdf=True)) if pdf else redirect(
                url_for('zeige_vokabelliste'))

        @self.app.route('/kommando/<cmd>')
        def antwort(cmd):
            """Fuehrt ein Kommando aus und leitet dann wieder weiter zu der aufrufenden Route"""
            self.setze_cmd_warte_auf_update(cmd, self.warte_zeit)
            return redirect(url_for(request_to_route(request.referrer)))

        @self.app.route('/get_aktuelle_uhrzeit')
        def get_aktuelle_uhrzeit():
            """Route fuer index"""
            return jsonify(self.data['aktuelle_uhrzeit'][:-7] if self.data.get('aktuelle_uhrzeit', False) else '0')

        @self.app.route('/get_aktuelle_und_neue_uhrzeit')
        def get_aktuelle_und_neue_uhrzeit():
            """Route fuer editor_lernuhr"""
            return jsonify({'aktuelle_uhrzeit': self.data['aktuelle_uhrzeit'][:-7],
                            'neue_uhrzeit': self.data['neue_uhrzeit'][:-7],
                            'neue_uhr': self.data['neue_uhr']})

        @self.app.route('/kommando_konsole/<cmd>')
        def kommando_konsole(cmd):
            """Modus, in dem die Kommandos direkt ueber die Adressleiste des Browsers eingegebenwerden koennen
                und die data als JSON im Browser angezeigt wird."""
            self.setze_cmd_warte_auf_update(cmd, self.warte_zeit)
            return jsonify(self.data)

    def update(self, daten: dict) -> None:
        """Funktion fuer die Protokoll-Klasse Beobachter"""
        self.data = daten

    def setze_cmd_warte_auf_update(self, cmd: str, wartezeit: float | int = 0.25, versuche: int = 20
                                   ) -> tuple[str, bool]:
        """ Wartet solange, bis der Controller self.cmd gelesen hat und self.data mit neuen Daten geupdated hat.
        Falls die Zahl der Versuche erreicht wurde, wird abgebrochen"""

        def kommando_ausgefuehrt(data: Any):
            self.cmd = False

        self.cmd = True
        self.event_manager.subscribe(EventTyp.KOMMANDO_EXECUTED, kommando_ausgefuehrt)
        self.event_manager.publish_event(EventTyp.NEUES_KOMMANDO, cmd)

        while self.cmd and versuche > 0:
            time.sleep(wartezeit)
            versuche -= 1
        self.event_manager.unsubscribe(EventTyp.KOMMANDO_EXECUTED, kommando_ausgefuehrt)
        self.cmd = False
        return cmd, self.cmd

    def run(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False)

    def start_server(self):
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
