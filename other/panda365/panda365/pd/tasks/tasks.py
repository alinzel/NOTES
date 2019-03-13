from blinker import signal

from pd.tasks import celery_app


@celery_app.task
def delay_signal(name, sender, **kwargs):
    """
    Send signal asynchronously in a task.

    This is useful for scheduling the signal to be sent at a specific time.

    E.g.::

        delay_signal.apply_async(
            countdown=50,
            args=('user_won', game),
            kwargs=...
        )
    """
    signal(name).send(sender, **kwargs)
