from flask import Flask, jsonify, render_template, request
from threading import Thread

from src.routes.flaskroutes import FlaskRoutes
from src.routes.index import IndexRoute

from src.classes.vokabelbox import Vokabelbox
from src.classes.lerneinheit import LerneinheitJapanisch

class FlaskView:

    def __init__(self) -> None:

        self.app = Flask(__name__, template_folder='templates')
        self.routes = FlaskRoutes(self.app)
        self.routes.register_routes()

        @self.app.route('/create_box', methods=['POST'])
        def create_box():
            titel = request.form['titel']
#            lernklasse = ...  # Hier die Lernklasse basierend auf der Benutzereingabe bestimmen
#            selektor =   # ...
            neue_box = Vokabelbox(titel,LerneinheitJapanisch)
            #vokabelboxen_repo.append(neue_box)
            print(f"Neue Box {neue_box}")
            return render_template('success.html')

        # route_index = IndexRoute('index.html')
        #route_index = IndexRoute(trainer, 'index.html')

        # @self.app.route('/')
        # @self.app.route('/index')
        # def index():
        #     return route_index.render_template()
        #
        # @self.app.route('/vokabelbox')
        # def vokabelbox():
        #     return route_vokabelbox.render_template()
        #
        # @self.app.route('/testfrage')
        # def testfrage():
        #     return route_testfrage.render_template()
        #
        # @self.app.route('/vokabeln')
        # def vokabeln():
        #     return route_vokabeln.render_template()

    def run(self):
        """Startet den Flask-Server in einem separaten Thread."""
        self.app.run(debug=False, use_reloader=False)

    def start_server(self):
        """Initialisiert und startet den Server im Hintergrund."""
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
