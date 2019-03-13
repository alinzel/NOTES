import arrow
from flask import current_app
from sqlalchemy.sql import text
from pd.facebook import signals
from pd.facebook.models import Post, PostPhoto
from pd.sqla import db
from .utils import get_item, upsert_user, sync_fb_static_file


@signals.fb_post_add.connect
def add_post(data, **kwargs):
    user = upsert_user(data)
    if 'link' in data:
        urls = [data['link']]
    elif 'photos' in data:
        urls = data['photos']
    else:
        urls = []
    # get image dimension
    # TODO: eventually this should be off-loaded to a celery task
    photos = [PostPhoto(url=sync_fb_static_file(url)) for url in urls]
    if 'created_time' in data:
        time = arrow.get(data['created_time'])
    else:
        time = kwargs['time']
    return Post.try_insert(
        is_active=False,
        publish_at=time,
        fb_id=data['post_id'],
        fb_page_id=kwargs['page_id'],
        created_at=time,
        message_translations={
            current_app.config['BABEL_FACEBOOK_LOCALE']: data.get('message'),
        },
        user=user,
        photos=photos,
    )


@signals.fb_post_edited.connect
def edit_post(data, **kwargs):
    return Post.fb_query(data['post_id']).update({
        Post.message_translations: text(
            '''jsonb_set(post.message_translations, '{{"{}"}}', '"{}"')
            '''.format(
                current_app.config['BABEL_FACEBOOK_LOCALE'],
                data.get('message', ''),
            )
        )
    }, synchronize_session='fetch')


@signals.fb_post_remove.connect
def remove_post(data, **kwargs):
    post = get_item(Post, data['post_id'])
    if post:
        db.session.delete(post)
        return True
