from dataclasses import asdict
from flask import Flask, jsonify, render_template, request, redirect, url_for
import inspect
from threading import Thread
import time


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
    'lernuhr' : {'ohne_speichern': lambda route: f"c0",
                 'mit_speichern': lambda route: f"@{route}"}
}

def request_to_route(adresse: str, default: str = 'index') -> str:
    """Ermittelt den String fuer """
    result = adresse.split('/')[-1] if adresse else default
    return result if result else default


class FlaskView:

    def __init__(self) -> None:

        self.app = Flask(__name__, template_folder='templates')

#        self.routes = FlaskRoutes(self.app)
#        self.routes.register_routes()

        self.data = {}
        self.cmd = None
        self.warte_zeit = 0.25      # siehe Funktion warte_auf_update()

        @self.app.route('/')
        def root():
            return redirect(url_for('index'))

        @self.app.route('/index')
        def index():
            # TODO verkuerzen durch Benutzung der Dictionarys oben
            print(f"{inspect.stack()[0].function =}")
            command = request.args.get('lernuhr', False)
            if command:
                if command == 'ohne_speichern':
                    print(f"{ command =}")
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
                                   kalkulations_zeit_datum=self.data['neue_uhr']['kalkulations_zeit'][:10],
                                   kalkulations_zeit_uhrzeit=self.data['neue_uhr']['kalkulations_zeit'][11:-7],
                                   start_zeit_datum=self.data['neue_uhr']['start_zeit'][:10],
                                   start_zeit_uhrzeit=self.data['neue_uhr']['start_zeit'][11:-7],
                                   tempo_wert=int(self.data['neue_uhr']['tempo'] // 1),
                                   tempo_kommastellen=round(self.data['neue_uhr']['tempo'] % 1, 3),
                                   neue_uhr=self.data['neue_uhr'])

        @self.app.route('/kommando/<cmd>')
        def antwort(cmd):
            self.setze_cmd_warte_auf_update(cmd, self.warte_zeit)
            return redirect(url_for(request_to_route(request.referrer)))

        @self.app.route('/get_aktuelle_uhrzeit')
        def get_aktuelle_uhrzeit():
            """Route fuer index"""
            print(f"{self.data = } {self.data['aktuelle_uhrzeit'][:-7] = }")
            return jsonify(self.data['aktuelle_uhrzeit'][:-7])

        @self.app.route('/get_aktuelle_und_neue_uhrzeit')
        def get_aktuelle_und_neue_uhrzeit():
            """Route fuer editor_lernuhr"""
            print(f" {self.data['aktuelle_uhrzeit']} ")
            return jsonify({'aktuelle_uhrzeit': self.data['aktuelle_uhrzeit'][:-7],
                            'neue_uhrzeit': self.data['neue_uhrzeit'][:-7],
                            'neue_uhr': f"{self.data['neue_uhr']}"}
                           )

        @self.app.route('/kommando_konsole/<cmd>')
        def kommando_konsole(cmd):
            """Modus, in dem die Kommandos direkt ueber die Adressleiste des Browsers eingegebenwerden koennen
                und die data als JSON im Browser angezeigt wird."""
            self.setze_cmd_warte_auf_update(cmd, self.warte_zeit)
            return jsonify(self.data)

    def setze_cmd_warte_auf_update(self, cmd: str, wartezeit: float | int = 0.25, versuche: int = 20
                                   ) -> tuple[str, str]:
        """ Wartet solange, bis der Controller self.cmd gelesen hat und self.data mit neuen Daten geupdated hat.
        Falls die Zahl der Versuche erreicht wurde, wird abgebrochen"""
        self.cmd = cmd
        while self.cmd and versuche > 0:
            time.sleep(wartezeit)
            versuche -= 1
        return cmd, self.cmd


    def run(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False)

    def start_server(self):
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
