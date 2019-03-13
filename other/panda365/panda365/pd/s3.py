import os
from boto import s3
from boto.s3.key import Key
from boto.s3.connection import OrdinaryCallingFormat
from flask import current_app
from flask_admin.contrib.fileadmin.s3 import S3Storage as BaseS3Storage
from werkzeug.utils import cached_property


class S3Storage(BaseS3Storage):

    def __init__(self, bucket_name, region, aws_access_key_id,
                 aws_secret_access_key):
        self.bucket_name = bucket_name
        self.region = region
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.separator = '/'

    @cached_property
    def bucket(self):
        connect_kwargs = dict(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )
        # this handles ssl check for bucket names with dots. See also:
        # https://github.com/boto/boto/issues/2836
        if '.' in self.bucket_name:
            connect_kwargs['calling_format'] = OrdinaryCallingFormat()
        connection = s3.connect_to_region(self.region, **connect_kwargs)
        return connection.get_bucket(self.bucket_name)

    def save_file(self, path, file_data, **headers):
        key = Key(self.bucket, path)
        if not headers.get('Content-Type'):
            headers['Content-Type'] = getattr(
                file_data, 'content_type', 'application/octet-stream')
        headers.setdefault('Cache-Control', 'max-age={}'.format(
            current_app.config['S3_OBJ_MAX_AGE']
        ))
        key.set_contents_from_file(file_data, headers)
        return 'https://{}/{}'.format(self.bucket_name, path)


class S3StorageExtension:

    def __init__(self):
        self.store = None

    def init_app(self, app):
        self.store = S3Storage(
            bucket_name=app.config['S3_BUCKET'],
            region=app.config['S3_REGION'],
            aws_access_key_id=app.config['AWS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_KEY_SECRET'],
        )

    def save_file(self, file_storage, directory=''):
        """
        :file_storage: an instance of werkzeug FileStorage
        """
        path = os.path.join(directory, file_storage.filename)
        self.store.save_file(path, file_storage)
        return 'https://' + os.path.join(self.store.bucket_name, path)

    def save_fp(self, fp, filename, directory=''):
        """
        Save the given fp in s3, returns the path in s3.

        The path generated as `directory/{uuid4}.{ext}`, where ext is
        extracted from filename. It also tries to guess the `content-type`
        from filename; if it fails, `application/octet-stream` is used.
        """
