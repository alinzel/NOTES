import arrow
from blinker import signal
from datadog import statsd
from flask import current_app
from pd.sqla import db


def parse_update(data):
    if data['object'] == 'page':
        for entry in data['entry']:
            time = arrow.get(entry['time'])
            for change in entry['changes']:
                parse_change(change, entry['id'], time)


def parse_change(change: dict, page_id: int, time: arrow.Arrow):
    """
    given a facebook webhook update, determine its subject(post, comment,
    etc) and action(add, remove, edit). Fire the signals accordingly.
    """
    if change['field'] == 'feed':  # we're only interested in feed
        data = change['value']
        if data['item'] in ('status', 'photo', 'post'):
            entity = 'post'
        elif data['item'] == 'comment':
            entity = 'comment'
        elif data['item'] == 'like':
            entity = 'like'
        elif data['item'] == 'reaction':
            return  # skip reactions for now
        else:  # pragma: no cover
            # no interest in other things
            current_app.logger.error(
                'unexpected fb_entity: %s; change: %s', data['item'], change)
            return

        results = signal(
            'fb_{}_{}'.format(entity, data['verb'])
        ).send(data, page_id=page_id, time=time)
        db.session.commit()
        for _, result in results:
            current_app.logger.info(
                'fb_event success: %s_%s - %s',
                entity, data['verb'], result
            )
            statsd.increment('fb_sync', tags=[
                'verb:{}'.format(data['verb']),
                'entity:{}'.format(entity),
            ])
