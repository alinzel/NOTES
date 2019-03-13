from flask import url_for
from pd.wish.factory import WishFactory, VoteFactory, TipFactory


def test_list_and_detail_pages(db_session, admin_client, user):
    # create some records to show
    wishes = WishFactory.create_batch(2)
    WishFactory(media=None)  # wish without media
    WishFactory(info_translations=None)
    for wish in wishes:
        VoteFactory(wish=wish, user=user)

    for model in (
        'wish', 'vote', 'tip',
    ):
        resp = admin_client.get(url_for('{}.index_view'.format(model)))
        assert resp.status_code == 200

    resp = admin_client.get(url_for('wish.details_view', id=wishes[0].id))
    assert resp.status_code == 200


def test_create_wish_random_tip(db_session, admin_client, user):
    url = url_for('wish.create_view')
    resp = admin_client.get(url)
    assert resp.status_code == 200
    # should warn if no tips are available
    assert '数据库里没有任何Tip' in resp.soup.select('.alert-warning')[0].text

    TipFactory.create_batch(2)
    resp = admin_client.get(url)
    assert resp.status_code == 200
    assert not resp.soup.select('.alert-warning')
