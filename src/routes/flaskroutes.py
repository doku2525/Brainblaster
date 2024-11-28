from dataclasses import dataclass, field
from flask import render_template, Flask

from src.routes.index import IndexRoute

@dataclass
class FlaskRoutes:
    app: Flask
    route_index: IndexRoute = field(default=IndexRoute('index.html'))

    def index(self):
        return self.route_index.render_template()

    def register_routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/index', 'index', self.index)