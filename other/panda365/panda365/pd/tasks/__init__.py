import logging

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import raven
from raven.contrib.celery import register_signal, register_logger_signal

from pd.utils import get_by_prefix
from .base import FlaskTask


def configure_celery(celery, app):
    celery.conf.update({
        k.lower(): v for k, v in get_by_prefix(app.config, 'CELERY_').items()})
    celery.flask_app = app
    # tasks
    import pd.tasks.tasks  # noqa
    import pd.tasks.monitoring  # noqa
    import pd.groupon.tasks  # noqa
    # beat schedules
    celery.visibility_timeout = celery.conf.broker_transport_options[
        'visibility_timeout']
    celery.conf.beat_schedule = {
        'check_for_imminent_batches': {
            'task': 'pd.groupon.tasks.check_for_imminent_batches',
            'schedule': celery.visibility_timeout,
        },
        'close_payment_processing_orders': {
            'task': 'pd.groupon.tasks.close_payment_processing_orders',
            'schedule': crontab(minute=10),
        }
    }

    # configure sentry
    client = raven.Client(
        **{k.lower(): v for k, v in
           get_by_prefix(app.config, 'SENTRY_').items()})
    register_logger_signal(client, loglevel=logging.ERROR)
    register_signal(client)


celery_app = Celery(task_cls=FlaskTask)
logger = get_task_logger(__name__)
