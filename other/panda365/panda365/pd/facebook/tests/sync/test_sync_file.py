import re
from unittest.mock import patch, Mock
import pytest
from pd.facebook.signal_handlers.utils import sync_fb_static_file


def test_sync_fb_static_file(app, png_path):
    with open(png_path, 'rb') as png:
        with patch('pd.facebook.signal_handlers.utils.sess') as mock_sess:
            resp = Mock(ok=True)
            resp.iter_content.return_value = [png.read()]
            mock_sess.get.return_value = resp
            s3_url = sync_fb_static_file('http://fake.com/foo.png')
            match = re.match(
                '^https:\/\/{}\/fb\/images\/(\w+)_(?P<width>\d+)_'
                '(?P<height>\d+).png$'.format(app.config['S3_BUCKET']),
                s3_url
            )
            assert match and match.groupdict() == dict(
                width='4', height='3')


@pytest.fixture
def mock_sess():
    with patch('pd.facebook.signal_handlers.utils.sess') as mock_sess:
        resp = Mock(
            ok=True,
        )
        resp.iter_content.return_value = [b'blah']
        resp.headers = {'Content-Type': None}
        mock_sess.get.return_value = resp
        yield mock_sess


def test_http_error(app_context, mock_sess):
    mock_sess.get.return_value = Mock(ok=False, status_code=404)
    assert not sync_fb_static_file('http://fake.com/foo.png')


@pytest.mark.parametrize('filename,expected_pattern', [
    ['hi', '^https:\/\/(.+)\/fb/(\w+)$'],
    ['hi.mp4', '^https:\/\/(.+)\/fb/videos/(\w+).mp4$'],
])
def test_ordinary_files(app_context, mock_sess, filename, expected_pattern):
    url = sync_fb_static_file('https://example.com/{}'.format(filename))
    assert re.match(expected_pattern, url)
