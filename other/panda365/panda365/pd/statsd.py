from datadog import statsd
from flask import request, g, request_started, request_finished
from pd.payment import signals as payment_signals


def _clean_name(val):
    if val:
        return val.replace('.', '_').replace(':', '_')
    else:
        return 'none'  # pragma: no cover


def _request_before(app, **extra):
    g._stats_timer = statsd.timed(
        metric='api.duration',
        tags=[
            'group:' + request.path.split('/')[1] or 'root',
            'endpoint:' + _clean_name(request.endpoint),
            'method:' + request.method,
        ],
        sample_rate=app.config['STATSD_SAMPLE_RATE'],
    )
    g._stats_timer.start()


def _request_finish(app, response, **extra):
    g._stats_timer.stop()


def install_hooks(app):
    statsd.namespace = 'pd'
    request_started.connect(_request_before, sender=app)
    request_finished.connect(_request_finish, sender=app)


def count_payment(payment):
    statsd.increment(
        'sales.payments.count', tags=[
            'vendor:{}'.format(payment.vendor.name),
            'status:{}'.format(payment.status.name),
        ]
    )


for name in dir(payment_signals):
    if name.startswith('payment_'):
        getattr(payment_signals, name).connect(count_payment)


@payment_signals.payment_succeeded.connect
def count_revenue(payment):
    statsd.increment(
        'sales.revenue', payment.amount,
        tags=[
            'currency:{}'.format(payment.currency),
            'vendor:{}'.format(payment.vendor),
        ],
    )
