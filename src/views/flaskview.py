from flask import Flask, jsonify, render_template, request, redirect, url_for
from threading import Thread
import time


class FlaskView:

    def __init__(self) -> None:

        self.app = Flask(__name__, template_folder='templates')

#        self.routes = FlaskRoutes(self.app)
#        self.routes.register_routes()

        self.data = {}
        self.cmd = None
        self.warte_zeit = 0.25      # siehe Funktion warte_auf_update()

        @self.app.route('/')
        @self.app.route('/index')
        def index():
            return render_template('index.html',
                                   data=enumerate(self.data['liste']),
                                   aktueller_index=self.data['aktueller_index'])

        @self.app.route('/kommando/<cmd>')
        def antwort(cmd):
            self.cmd = cmd
            self.warte_auf_update()
            return redirect(url_for('index'))

    def warte_auf_update(self):
        """ Wartet solange, bis der Controller self.cmd gelesen hat und self.data mit neuen Daten geupdated hat."""
        while self.cmd:
            time.sleep(self.warte_zeit)

    def run(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False)

    def start_server(self):
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
