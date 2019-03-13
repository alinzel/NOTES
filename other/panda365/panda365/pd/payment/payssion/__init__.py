from .client import Client


class Extension:
    def __init__(self, app=None):
        self.client = None
        self.app = app
        if app:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        self.client = Client(
            app.config['PAYSSION_API_KEY'],
            app.config['PAYSSION_API_SECRET'],
            app.config['PAYSSION_IS_SANDBOX'],
        )
