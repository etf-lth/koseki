from flask.blueprints import Blueprint


class KosekiPlugin:
    def __init__(self, app, core, storage):
        self.app = app
        self.core = core
        self.storage = storage

    def config(self) -> dict:
        pass

    def create_blueprint(self) -> Blueprint:
        pass
