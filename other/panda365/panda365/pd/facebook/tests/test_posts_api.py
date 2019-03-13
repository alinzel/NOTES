import arrow
import pytest
from pd.test_utils import assert_dict_like, assert_sorted_by
from pd.bookmark.factory import BookmarkFactory
from pd.facebook.api.posts import liked_posts_list
from pd.facebook.factory import (
    PostFactory, PostPhotoFactory, UserFactory, PresalePostFactory,
    OnsalePostFactory,
)
from pd.facebook.models import Post, Country


pytestmark = pytest.mark.db


def test_posts_list(client):
    posts = PostFactory.create_batch(5)
    PresalePostFactory()
    resp = client.get('/v1/posts/')
    assert resp.status_code == 200
    # should only include normal posts, without any shopping post
    assert {o['id'] for o in resp.json['objects']} == {p.id for p in posts}
    assert_sorted_by(resp.json['objects'], '-created_at')
    obj = resp.json['objects'][0]
    post = Post.query.get(obj['id'])
    user = post.user
    assert_dict_like(obj, {
        'created_at': post.created_at.isoformat(),
        'gid': post.gid,
        'fb_id': post.fb_id,
        'comments_num': 0,
        'likes_num': 0,
        'photo_urls': post.photo_urls,
        'message': post.message,
        'media_type': 'post',
        '_type': 'post',
        'sale_on': None,
        'price': None,
        'currency': None,
        'user': {
            'id': user.id,
            'gid': user.gid,
            'fb_id': user.fb_id,
            'name': user.name,
            'icon_url': user.icon_url,
        }
    })
    # product info
    info = post.info_translations['en']
    k, v = info.split(':')
    assert obj['info'] == [{
        'name': k.strip(),
        'value': v.strip(),
    }]


def test_message_translation(app, monkeypatch, client):
    monkeypatch.setitem(app.config, 'BABEL_SUPPORTED_LOCALES', ['en', 'zh_cn'])
    en = 'english'
    zh = '中文'
    PostFactory(message_translations={
        'en': en,
        'zh_cn': zh,
    })

    resp = client.get('/v1/posts/')
    assert resp.json['objects'][0]['message'] == en

    resp = client.get('/v1/posts/', headers={
        'Accept-Language': 'zh-cn;q=0.8, zh;q=0.6',
    })
    assert resp.json['objects'][0]['message'] == zh


def test_visible_posts(client):
    '''
    only posts that are:
        - active
        - whose publish_at <= now
    are shown to users
    '''
    inactive_post = PostFactory(is_active=False)
    assert not inactive_post.is_visible
    # active, but publish time is yet to come
    draft_post = PostFactory(publish_at=arrow.utcnow().replace(hours=1))
    assert not draft_post.is_visible
    # active and published
    post = PostFactory()
    assert post.is_visible

    resp = client.get('/v1/posts/')
    assert len(resp.json['objects']) == 1
    assert resp.json['objects'][0]['id'] == post.id, (
        inactive_post.id, draft_post.id
    )


def test_liked_posts_list(client):
    # should require auth
    assert liked_posts_list._auth_required

    # 4 posts in db: a post nobody likes; a post liked by u1;
    # 2 posts liked by u2, one of which is inactive
    user1, user2 = UserFactory.create_batch(2)
    _, u1_liked, u2_liked, u2_liked_inactive = PostFactory.create_batch(4)
    u1_liked.add_like(user_id=user1.id)
    u2_liked.add_like(user_id=user2.id)
    u2_liked_inactive.add_like(user_id=user2.id)
    u2_liked_inactive.is_active = False

    client.login(user2)
    resp = client.get('/v1/posts/liked/')
    assert resp.status_code == 200, resp.text
    # only my liked posts should be returned
    assert len(resp.json['objects']) == 1
    returned_post = resp.json['objects'][0]
    assert returned_post['id'] == u2_liked.id


def test_shopping_posts_list(client):
    # 4 posts in db: a shopping post, an onsale post, an inactive shopping
    # post, a fb post
    PostFactory()
    onsale_post = OnsalePostFactory()
    presale_post = PresalePostFactory()
    PresalePostFactory(is_active=False)

    resp = client.get('/v1/posts/shopping/')
    assert resp.status_code == 200, resp.text
    # only the 2 active shopping posts should be returned
    assert len(resp.json['objects']) == 2
    objs_by_id = {o['id']: o for o in resp.json['objects']}
    # onsale post returned
    returned_post = objs_by_id[onsale_post.id]
    assert onsale_post.is_visible

    vendor_link = onsale_post.vendor_links[0]
    assert_dict_like(returned_post['vendor_links'][0], {
        'url': vendor_link.url,
        'price': vendor_link.price,
        'currency': {
            'code': vendor_link.currency.code,
            'symbol': vendor_link.currency.symbol,
        },
        'vendor': {
            'name': vendor_link.vendor.name,
            'logo_url': vendor_link.vendor.logo_url,
        }
    })

    # presale post
    returned_post = objs_by_id[presale_post.id]
    assert_dict_like(returned_post, {
        'sale_on': presale_post.sale_on.isoformat(),
        'price': presale_post.price,
        'currency': {
            'code': presale_post.currency.code,
            'symbol': presale_post.currency.symbol,
        }
    })


def test_bookmarked_posts_list(client):
    # 3 posts in db: a normal post, one bookmarked by u1, one bookmarked by u2
    u1, u2 = UserFactory.create_batch(2)
    PostFactory()
    post_bookmarked = PostFactory()
    BookmarkFactory(post=post_bookmarked, user=u1)
    post2 = PostFactory()
    BookmarkFactory(post=post2, user=u2)

    client.login(u1)
    # should only return post bookmarked by u1
    resp = client.get('/v1/posts/bookmarked/')
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 1
    assert resp.json['objects'][0]['id'] == post_bookmarked.id


def _get_post_ids(client, url, *media_types):
    """
    call the posts list API, applying the given media type filter, return
    the id of the posts
    """
    resp = client.get(
        url,
        query_string='&'.join('media_type={}'.format(m) for m in media_types))
    assert resp.status_code == 200
    return {o['id'] for o in resp.json['objects']}


@pytest.mark.parametrize('url,post_factory', [
    ['/v1/posts/', PostFactory],
    ['/v1/posts/shopping/', PresalePostFactory],
])
def test_media_type_filter(client, url, post_factory):
    photo_post = post_factory()
    PostPhotoFactory(url='foo.png', post=photo_post)
    gif_post = post_factory()
    PostPhotoFactory(url='foo.gif', post=gif_post)
    video_post = post_factory()
    PostPhotoFactory(url='foo.mp4', post=video_post)

    # should be able to filter posts by media_type
    assert _get_post_ids(client, url, 'gif') == {gif_post.id}
    # should be able to filter multiple media_types
    assert _get_post_ids(client, url, 'gif', 'photo') == {
        gif_post.id, photo_post.id}


def test_country_filter(client):
    # country filter is only applicable to shopping posts list API
    url = '/v1/posts/shopping/'

    PostFactory()  # normal posts do not have a country
    malaysia_post = PresalePostFactory(country=Country.MY)
    indonisia_post = PresalePostFactory(country=Country.ID)

    resp = client.get(url)
    assert resp.status_code == 200
    assert {o['id'] for o in resp.json['objects']} == {
        malaysia_post.id, indonisia_post.id}

    # should return shopping posts in the country only
    resp = client.get(url, query_string={'country': 'ID'})
    assert resp.status_code == 200
    assert {o['id'] for o in resp.json['objects']} == {indonisia_post.id}
