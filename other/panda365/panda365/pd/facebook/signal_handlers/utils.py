from contextlib import closing
import mimetypes
from tempfile import TemporaryFile
import uuid
import os
from flask import current_app
from furl import furl
from requests import Session
from PIL import Image
from pd.ext import s3ext
from pd.sqla import logger
from pd.facebook.models import User


def get_item(cls, fb_id):
    item = cls.fb_query(fb_id).first()
    if not item:
        logger.warn('%s not found by fb_id "%s"', cls.__name__, fb_id)
    return item


def upsert_user(data):
    return User.upsert(
        str(data['sender_id']),
        # if the user has no name, facebook omits the key "sender_name"
        name=data.get('sender_name', ''),
    )


sess = Session()


def sync_fb_static_file(fb_url):
    """
    given a url to a facebook static file, like an image or a video, fetch
    it and upload to s3, return the its url in s3. If the file is an image,
    its dimension is added to the returned url as query parameters.

    For example::

        >>> sync_fb_static_file('https://scontent.xx.fbcdn.net/v/t1.0-9/18814166_1691460984489301_6965084884908224053_n.jpg')  # noqa
        "https://static-dev.panda365.com/fb/images/uuid_800_600.jpg?"

    The path is generated as `{type}s/{uuid4}(_{width}_{height}).{ext}`,
    where `ext` is extracted from filename. It also tries to guess the
    `content-type` from filename; if it fails, `application/octet-stream` is
    used. If the file is an image, its width and height are extracted and
    appended to the filename.
    """
    if not fb_url:
        return
    with TemporaryFile() as tmp_fp:
        with closing(sess.get(fb_url, stream=True)) as resp:
            if not resp.ok:
                current_app.logger.warn(
                    'fail to fetch fb static file %s: %s',
                    fb_url, resp.status_code)
                return
            for chunk in resp.iter_content(1024):
                tmp_fp.write(chunk)
            tmp_fp.seek(0)
        # generate s3 path
        s3_path = ['fb']
        # guess content type
        f_url = furl(fb_url)
        filename = f_url.path.segments[-1]
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = resp.headers.get('Content-Type', None)
        if content_type:
            s3_path.append(content_type.split('/')[0] + 's')
        # construct s3 filename
        s3_name = [uuid.uuid4().hex]
        # image dimension
        if content_type and content_type.startswith('image'):
            # figure out dimension
            im = Image.open(tmp_fp)
            s3_name.append('_{}_{}'.format(im.width, im.height))
            tmp_fp.seek(0)
        # extension
        parts = filename.split('.')
        if len(parts) > 1:
            s3_name.append('.' + parts[-1])
        # full s3 path
        s3_path.append(''.join(s3_name))  # filename
        s3_path = os.path.join(*s3_path)
        # upload to s3
        return s3ext.store.save_file(
            s3_path, tmp_fp, **{'Content-Type': content_type})
