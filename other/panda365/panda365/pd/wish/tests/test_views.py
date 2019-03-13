from flask import url_for
from pd.constants import Country
from pd.wish.factory import WishFactory


def get_url_params(wish, **kwargs):
    default = dict(id=wish.id, uid=1334423, country='MY')
    default.update(**kwargs)
    return default


def test_wish_detail_page(db_session, client):
    wish = WishFactory(prices__country=Country.MY)

    resp = client.get(url_for('wish_pages.detail', **get_url_params(wish)))
    assert resp.status_code == 200

    # errors
    for error_param, expected_code in (
        ({'uid': None}, 400),
        ({'country': 'JP'}, 404),
        ({'id': 123123}, 404),
    ):
        resp = client.get(
            url_for('wish_pages.detail', **get_url_params(wish, **error_param))
        )
        assert resp.status_code == expected_code
