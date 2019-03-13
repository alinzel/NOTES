from flask import url_for
from pd.groupon.factory import (
    BatchFactory, ProductFactory, OrderFactory, CategoryFactory)
from pd.groupon.models import Batch
from unittest.mock import patch
import pytest
from pd.groupon.models.order import OrderStatus


pytestmark = pytest.mark.db


def test_product_admin(admin_client):
    product = ProductFactory()
    product2 = ProductFactory(media=None)

    resp = admin_client.get('/admin/product/')
    assert resp.status_code == 200

    for p in (product, product2):
        resp = admin_client.get('/admin/product/details/', query_string={
            'id': p.id,
        })
        assert resp.status_code == 200


def _get_batch_form_data(**kwargs):
    product = ProductFactory()
    category = CategoryFactory()
    data = {
        'product': product.id,
        'category': category.id,
        'country': 'ID',
        'price': 1,
        'currency': 'USD',
        'market_price': 1,
        'market_currency': 'USD',
        'shipping_price': 1,
        'total_shares': 2,
        'start_at': '2017-01-01 00:00:00',
        'end_at': '2017-01-09 00:00:00',
    }
    data.update(kwargs)
    return data


def test_batch_admin(admin_client):
    data = _get_batch_form_data()
    resp = admin_client.post('/admin/batch/new/', data=data)
    assert resp.status_code == 302
    batch = Batch.query.first()
    assert batch
    # should create the first game automatically when the batch is created
    assert len(batch.games) == 1

    # 一些字段在批次创建后不能修改
    resp = admin_client.get('/admin/batch/edit/', query_string={
        'id': batch.id,
    })
    assert resp.status_code == 200
    for k in ('country', 'price', 'currency', 'shipping_price'):
        assert resp.soup.find(id=k).attrs['disabled'] == ''

    resp = admin_client.post('/admin/batch/edit/', query_string={
        'id': batch.id,
    }, data=data)
    assert resp.status_code == 302
    # should not create any game when editing batch
    assert len(batch.games) == 1

    resp = admin_client.post('/admin/batch/edit/?id=1',
                             data=_get_batch_form_data())
    assert resp.status_code == 302

    resp = admin_client.get('/admin/batch/')
    assert resp.status_code == 200


def test_game_admin(admin_client):
    batch = BatchFactory(total_shares=3)
    game = batch.create_game()

    resp = admin_client.get('/admin/game/')
    assert resp.status_code == 200

    with patch(
        'pd.groupon.models.game.Batch.check_game_finish'
    ) as mock_check_game_finish:
        resp = admin_client.post('/admin/game/edit/', query_string={
            'id': game.id,
        }, data={
            'market_price': 1,
            'market_currency': 'USD',
            'shipping_price': game.shipping_price,
            'start_at': game.start_at.format(),
            'end_at': game.end_at.format(),
            'direct_buy_url': 'blah',
            'total_shares': 3,
            'left_shares': 0,
        })
        assert resp.status_code == 302, resp.soup.select('.input-errors')
        assert mock_check_game_finish.called
        assert mock_check_game_finish.call_args[0] == (game,)


@pytest.mark.parametrize('start_at, end_at, expected_success', [
    ['2017-01-01 00:00:00', '2017-01-01 00:10:00', True],
    ['2017-01-01 00:00:00', '2017-01-01 00:00:00', False],
    ['2017-01-01 00:00:00', '2016-01-01 00:00:00', False],
    ['', '', False],
])
def test_validate_end_at(
        admin_client, start_at, end_at, expected_success):
    resp = admin_client.post(
        url_for('batch.create_view'),
        data=_get_batch_form_data(
            start_at=start_at,
            end_at=end_at,
        )
    )
    if expected_success:
        assert resp.status_code == 302
    else:
        assert b'error' in resp.data


def test_order_admin(admin_client, user, db_session):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    OrderFactory(user=user, game=game)
    resp = admin_client.get('/admin/order/')
    # test product link
    assert resp.status_code == 200
    assert b'href="/admin/product/?flt_id_equals=' in resp.data


@pytest.mark.parametrize('from_status, category', [
    ['processing', 'success'],
    ['paid', 'info'],
    ['shipped', 'info'],
])
def test_order_actions(
        user, admin_client, db_session,
        from_status, category):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    order = OrderFactory(
        user=user,
        game=game,
        status=OrderStatus[from_status],
    )
    resp = admin_client.action('order', 'shipped', order.id)
    messages = resp.page.get_messages_by(category=category)
    assert len(messages) == 1
    if category == 'success':
        assert 'successfully' in messages[0]
        assert order.status == OrderStatus['shipped']
    else:
        assert 'no order can be set' in messages[0]
        assert order.status == OrderStatus[from_status]
