import importlib


def configure_payments(app):
    for vendor in app.config['PAYMENT_ENABLED_VENDORS']:
        mod = importlib.import_module('pd.payment.{}.api'.format(vendor))
        app.register_blueprint(mod.api)
