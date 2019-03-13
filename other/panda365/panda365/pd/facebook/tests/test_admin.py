import arrow
from unittest.mock import Mock
import pytest
from pd.facebook.admin import PostAdmin
from pd.facebook.factory import (
    CommentFactory, UserFactory, PostFactory, PostPhotoFactory, ReplyFactory,
    LikeFactory, PresalePostFactory, OnsalePostFactory,
)
from pd.facebook.models import Post, MediaType, Country
from pd.vendor.factory import VendorFactory


pytestmark = pytest.mark.db


@pytest.mark.parametrize('is_created', [True, False])
def test_set_user(app, db_session, is_created):
    admin = PostAdmin(Post, db_session)
    UserFactory(name=app.config['PAGE_USER_NAME'])
    post = Post()
    admin.on_model_change(
        form=Mock(),
        model=post,
        is_created=is_created,
    )
    assert bool(post.user) == is_created


def test_post_detail_view(admin_client):
    post = PostFactory(photos=[PostPhotoFactory.build()])
    resp = admin_client.get('/admin/post/details/?id={}'.format(post.id))
    assert resp.status_code == 200


def test_list_views(admin_client):
    # setup a bunch of staff to show
    post = PostFactory()
    PostFactory(message_translations=None)
    PostFactory(photos=[PostPhotoFactory.build()])
    n = len(Country)
    presale_posts = PresalePostFactory.create_batch(n)
    onsale_posts = OnsalePostFactory.create_batch(n)
    comment = CommentFactory()
    reply = ReplyFactory()
    CommentFactory(photo_url=None)
    ReplyFactory(photo_url=None)
    like = LikeFactory()

    for ep in (
        'post', 'postphoto', 'reply', 'like', 'comment', 'normal-post',
    ):
        resp = admin_client.get('/admin/{}/'.format(ep))
        assert resp.status_code == 200

    for ep, model in (
        ('post', post),
        ('normal-post', post),
        ('comment', comment),
        ('reply', reply),
        ('like', like),
    ):
        resp = admin_client.get(
            '/admin/{}/details/?id={}'.format(ep, model.id))
        assert resp.status_code == 200

    for ep, posts in (
        ('presale_post', presale_posts),
        ('onsale_post', onsale_posts),
    ):
        for country in Country:
            resp = admin_client.get('/admin/{}_{}/'.format(ep, country.name))
            assert resp.status_code == 200
        for p in posts:
            resp = admin_client.get(
                '/admin/{}_{}/details/?id={}'.format(
                    ep, p.country.name, p.id))
            assert resp.status_code == 200


def _get_post_data(**kwargs):
    return dict({
        'comments_num': 0,
        'likes_num': 0,
        'publish_at': '2017-05-01 00:00:00',
        'is_active': True,
    }, **kwargs)


def test_edit_message(admin_client):
    post = PostFactory()
    url = '/admin/normal-post/edit/?id={}'.format(post.id)

    resp = admin_client.get(url)
    assert resp.status_code == 200

    # can update message translations
    content = 'new content'
    resp = admin_client.post(url, data=_get_post_data(**{
        'message_translations-0-locale': 'en',
        'message_translations-0-content': content,
    }))
    assert resp.status_code == 302
    assert post.message_translations['en'] == content

    # cannot give the same locale twice
    resp = admin_client.post(url, data=_get_post_data(**{
        'message_translations-0-locale': 'en',
        'message_translations-0-content': content,
        'message_translations-1-locale': 'en',
        'message_translations-1-content': 'blah',
    }))
    assert resp.status_code == 200
    assert post.message_translations['en'] == content

    # can set message to empty
    resp = admin_client.post(url, data=_get_post_data(**{
        'message_translations-0-locale': 'en',
        'message_translations-0-content': content,
        # this deletes zh-cn
    }))
    assert resp.status_code == 302
    assert 'zh_cn' not in post.message_translations


def _get_vendor_link_data(vendor):
    return {
        'vendor_links-0-vendor': vendor.id,
        'vendor_links-0-price': 1,
        'vendor_links-0-currency': 'USD',
        'vendor_links-0-url': 'blah',
    }


@pytest.fixture
def country():
    return Country.ID


def test_presale_post(admin_client, country):
    # create
    data = _get_post_data(sale_on='2017-01-01', price='10', currency='MYR')
    url = '/admin/presale_post_{}'.format(country.name)
    resp = admin_client.post(url + '/new/', data=data)
    assert resp.status_code == 302
    post = Post.query.first()
    assert post and post.is_shopping
    last_updated_at = post.updated_at
    # edit
    vendor = VendorFactory()
    data.update(_get_vendor_link_data(vendor))
    resp = admin_client.post(url + '/edit/?id={}'.format(post.id), data=data)
    assert resp.status_code == 302
    # should update some fields to make the post go sale
    assert post.updated_at > last_updated_at
    assert post.is_shopping and not post.sale_on
    assert post.price == data['vendor_links-0-price']
    assert post.currency == data['vendor_links-0-currency']
    assert len(post.vendor_links) == 1
    assert post.vendor_links[0].url == data['vendor_links-0-url']
    assert post.country == country


def test_onsale_post(admin_client, country):
    vendor = VendorFactory()
    data = _get_post_data(**_get_vendor_link_data(vendor))
    url = '/admin/onsale_post_{}'.format(country.name)
    # create
    resp = admin_client.post(url + '/new/', data=data)
    assert resp.status_code == 302
    post = Post.query.first()
    assert post and post.is_shopping
    assert post.vendor_links
    # edit: remove vendor link
    data.update({
        'del-vendor_links-0': 'on',
        'vendor_links-0-id': post.vendor_links[0].id,
    })
    resp = admin_client.post(url + '/edit/?id={}'.format(post.id), data=data)
    assert resp.status_code == 302
    # if vendor link is removed, sale_on should be set
    assert post.sale_on == arrow.utcnow().shift(weeks=1).date()
    assert post.country == country


def test_post_list_view(admin_client, country, model_admin_render_mock):
    # create a product in each country
    n = len(Country)
    PresalePostFactory.create_batch(n)
    OnsalePostFactory.create_batch(n)
    # should only return products in the given country
    for ep in ('onsale_post', 'presale_post'):
        admin_client.get('/admin/{}_{}'.format(ep, country.name))
        _, kwargs = model_admin_render_mock.call_args
        rendered_posts = kwargs['data']
        assert len(rendered_posts) == 1
        assert rendered_posts[0].country == country
        model_admin_render_mock.reset()


@pytest.mark.parametrize('image_ext', ['gif', 'png'])
def test_create_post(image_ext, admin_client, gif_path, png_path):
    if image_ext == 'gif':
        file_path = gif_path
    elif image_ext == 'png':
        file_path = png_path
    else:  # pragma: no cover
        assert False
    with open(file_path, 'rb') as fp:
        data = _get_post_data(**{
            'photos-0-url': fp,
            'photos-0-id': '',
        })
        resp = admin_client.post('/admin/normal-post/new/', data=data)
    assert resp.status_code == 302
    post = Post.query.first()
    assert post.photo_urls[0].endswith(image_ext)
    if image_ext == 'gif':
        # a cover should be created
        assert len(post.photo_urls) == 2
        assert post.photo_urls[1].endswith('jpeg')
        assert post.media_type == MediaType.gif
    elif image_ext == 'png':
        assert len(post.photo_urls) == 1
        assert post.media_type == MediaType.photo
    else:  # pragma: no cover
        assert False
