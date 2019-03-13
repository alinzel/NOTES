import arrow
from pd.facebook import signals
from pd.facebook.models import Post, Comment
from .utils import get_item, upsert_user


def _get_parent(data):
    if 'post_id' in data:
        return get_item(Post, data['post_id'])
    else:
        return get_item(Comment, data['comment_id'])


def _make_like_fb_id(parent, data):
    return '{}_{}'.format(parent.fb_id, data['sender_id'])


@signals.fb_like_add.connect
def add_like(data, **kwargs):
    parent = _get_parent(data)
    if parent:
        user = upsert_user(data)
        if 'created_time' in data:
            time = arrow.get(data['created_time'])
        else:
            time = kwargs['time']
        return parent.add_like(
            fb_id=_make_like_fb_id(parent, data),
            created_at=time,
            user=user,
        )


@signals.fb_like_remove.connect
def remove_like(data, **kwargs):
    parent = _get_parent(data)
    if parent:
        return parent.remove_like(fb_id=_make_like_fb_id(parent, data))
