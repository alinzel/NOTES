from unittest.mock import patch
from requests import ConnectTimeout
import pytest
from pd.commands import (
    urls, create_token, sync_photos, create_guest_account)
from pd.facebook.factory import PostFactory, PostPhotoFactory
from pd.guest.models import GuestUsers


def test_urls(app_context):
    assert urls()


def test_create_token(app_context, user):
    assert create_token(user.id)
    with patch('pd.commands.click.get_current_context') as m:
        ctx = m.return_value
        ctx.fail.side_effect = RuntimeError
        with pytest.raises(RuntimeError):
            assert not create_token(123123123)
        assert 'does not exist' in str(ctx.fail.call_args)


def test_sync_photos(db_session, app_context):
    post = PostFactory()
    urls = (
        'https://scontent.xx.fbcdn.net/v/t1.0-9/18838962_1692703134365086_7191051565314626653_n.jpg?_nc_ad=z-m&oh=12a8094cb21a6e08d0c000fc0a7d350a&oe=59E4CD56&_w=800&_h=800',  # noqa
        'https://fb-s-b-a.akamaihd.net/h-ak-fbx/v/t1.0-9/18813538_1692703291031737_3591740364485979938_n.jpg?_nc_ad=z-m&oh=91f29a905e9525222700f05d1cf9bd09&oe=59AA116F&__gda__=1503569796_e6bf26e3ca1e9a222fdfb88802607829&_w=800&_h=800',  # noqa
        'https://scontent.xx.fbcdn.net/v/t1.0-9/18839281_1691934804441919_5520943738726579089_n.jpg?oh=6e7d851714b6e8d0e07bf2a0fc2132ad&oe=59DEAEEB&_w=800&_h=800',  # noqa
        'https://scontent.xx.fbcdn.net/v/t1.0-9/18486371_1686691498299583_7325259982133402299_n.jpg?_nc_ad=z-m&oh=e1ec647c7aea9547f24e3c9360720c5e&oe=59A74744',  # noqa
        'scontent.xx.fbcdn.net/v/t1.0-9/18486371_1686691498299583_7325259982133402299_n.jpg?_nc_ad=z-m&oh=e1ec647c7aea9547f24e3c9360720c5e&oe=59A74744',  # noqa
        '//foo/bar.jpg'
    )
    for url in urls:
        PostPhotoFactory(post=post, url=url)
    with patch(
        'pd.commands.sync_fb_static_file',
            return_value='http://foo/bar_10_20.png'):
        # should process all urls
        assert sync_photos() == len(urls)
        assert sync_photos() == 0


def test_sync_photos_errors(db_session, app_context):
    post = PostFactory()
    PostPhotoFactory(post=post, url='http://foo/bar.jpg')
    with patch('pd.commands.sync_fb_static_file', return_value=None) as mock:
        assert sync_photos() == 0
        mock.side_effect = ConnectTimeout
        assert sync_photos() == 0


def test_create_guest_account(db_session):
    create_guest_account('helms', '123')
    user = GuestUsers.query.filter().first()
    assert user.account == 'helms'
