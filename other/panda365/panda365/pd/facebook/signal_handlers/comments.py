import arrow
from pd.facebook import signals
from pd.facebook.models import Comment, Post
from .utils import get_item, upsert_user, sync_fb_static_file


def _get_parent(data):
    if data['parent_id'] == data['post_id']:
        cls = Post
    else:
        cls = Comment
    return get_item(cls, data['parent_id'])


@signals.fb_comment_add.connect
def add_comment(data, **kwargs):
    parent = _get_parent(data)
    if parent:
        user = upsert_user(data)
        if 'created_time' in data:
            time = arrow.get(data['created_time'])
        else:
            time = kwargs['time']
        return parent.add_comment(
            fb_id=data['comment_id'],
            created_at=time,
            message=data.get('message'),
            photo_url=sync_fb_static_file(data.get('photo')),
            user=user,
        )


@signals.fb_comment_edited.connect
def edit_comment(data, **kwargs):
    return Comment.fb_query(data['comment_id']).update({
        'message': data.get('message'),
    })


@signals.fb_comment_remove.connect
def remove_comment(data, **kwargs):
    parent = _get_parent(data)
    if parent:
        return parent.remove_comment(fb_id=data['comment_id'])
