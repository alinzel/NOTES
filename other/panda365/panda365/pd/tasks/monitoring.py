from celery import signals
from datadog import statsd


@signals.after_task_publish.connect
def count_queued(sender, **kwargs):
    # sender is the name of the task
    statsd.increment(
        'celery.tasks',
        tags=[
            'task:{}'.format(sender),
            'state:queued',
        ]
    )


@signals.task_prerun.connect
def start_task_timer(sender, **kwargs):
    sender._stats_timer = statsd.timed(
        metric='celery.tasks.duration',
        tags=['task:{}'.format(sender.__name__)],
    )
    sender._stats_timer.start()


@signals.task_postrun.connect
def count_processed(sender, **kwargs):
    # sender is task obj
    tags = ['task:{}'.format(sender.__name__)]
    if 'state' in kwargs:
        statsd.increment(
            'celery.tasks',
            tags=tags + ['state:{}'.format(kwargs['state'].lower())]
        )
    if hasattr(sender, '_stats_timer'):
        sender._stats_timer.stop()
