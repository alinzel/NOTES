from pd.constants import Country
from pd.facebook.factory import UserFactory
from pd.groupon.api import order_create, orders_list
from pd.groupon.factory import (
    AddressDictFactory, BatchFactory, OrderFactory, CategoryFactory,
    BatchSpecFactory, SpecOptionFactory, ProductFactory)
from pd.groupon.models import Game, Order
from pd.groupon.models.order import OrderStatus
from pd.groupon.schema import OrderCreateSchema
from pd.payment import signals as payment_signals
from pd.payment.factory import PaymentFactory
from pd.test_utils import assert_dict_like, assert_sorted_by, Any
import arrow


def test_auth():
    for ep in (
        order_create,
        orders_list,
    ):
        assert ep._auth_required


def _assert_game_schema(data, game):
    assert_dict_like(data, dict(
        id=game.id,
        batch_id=game.batch_id,
        country=game.country.name,
        price=float(game.price),
        currency=dict(code=str(game.currency.code)),
        market_price=float(game.market_price),
        market_currency=dict(code=str(game.currency.code)),
        shipping_price=float(game.shipping_price),
        created_at=game.created_at.isoformat(),
        start_at=game.start_at.isoformat(),
        end_at=game.end_at.isoformat(),
        left_shares=game.left_shares,
        sold_shares=game.sold_shares,
        total_shares=game.total_shares,
        direct_buy_url=game.direct_buy_url,
        issue_id=game.issue_id,
    ))
    product = game.product
    assert_dict_like(data['product'], dict(
        title=product.title,
        media_urls=product.media_urls,
    ))


def _assert_order_schema(data, order):
    assert_dict_like(data, dict(
        id=order.id,
        created_at=order.created_at.isoformat(),
        email=order.email,
        game_id=order.game_id,
        status=order.status.name,
        # address
        full_name=order.full_name,
        complete_address=order.complete_address,
        postcode=order.postcode,
        city=order.city,
        province=order.province,
        phone=order.phone,
        spec=order.spec,
    ))


def test_games_api(db_session, client, user):
    # 2 games in each country
    for c in (Country.ID, Country.MY):
        for _ in range(2):
            b = BatchFactory(country=c)
            b.create_game()
    db_session.commit()
    url = '/v1/group/games/'

    # should support filter by country
    resp = client.get(url, query_string=dict(country='MY'))
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 2
    # sort order
    assert_sorted_by(
        resp.json['objects'],
        key=lambda o: (o['sort_weight'], o['product']['id'],),
        reverse=True
    )
    # schema
    data = resp.json['objects'][0]
    game = Game.query.get(data['id'])
    assert game.is_running
    _assert_game_schema(data, game)
    product = game.product
    assert_dict_like(data['product'], dict(
        title=product.title,
        description=product.description,
        info=Any(list),
    ))

    # it works even if country is not given
    resp = client.get(url)
    assert resp.status_code == 200

    # it works even if description is not given
    product = ProductFactory(description=None)
    batch = BatchFactory(product=product)
    batch.create_game()
    db_session.flush()
    resp = client.get(url)
    assert resp.status_code == 200
    assert not resp.json['objects'][0]['product']['description']


def test_game_detail(db_session, client):
    u1, u2 = UserFactory.create_batch(2)
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    # other people's order
    OrderFactory(user=u2, game=game, status=OrderStatus.paid)
    order = OrderFactory(user=u1, game=game)
    url_tpl = '/v1/group/games/{}'
    # game detail API
    resp = client.get(url_tpl.format(game.id))
    assert resp.status_code == 200
    _assert_game_schema(resp.json, game)
    assert resp.json['order'] is None
    # if user is logged-in, should return order data
    client.login(u1)
    resp = client.get(url_tpl.format(game.id))
    assert resp.status_code == 200
    _assert_order_schema(resp.json['order'], order)
    # paid order
    assert len(resp.json['users']) == 1

    # game does not exist
    resp = client.get(url_tpl.format(123123))
    assert resp.status_code == 404


def test_game_batch_spec(db_session, client):
    batch = BatchFactory()
    game = batch.create_game()
    options = SpecOptionFactory.build_batch(2)
    bs = BatchSpecFactory(batch_id=batch.id, options=options)
    db_session.commit()
    url_tpl = '/v1/group/games/{}'
    # game detail API
    resp = client.get(url_tpl.format(game.id))
    assert resp.status_code == 200
    assert resp.json['specs'][0]['options'][0] == str(options[0])
    assert resp.json['specs'][0]['spec'] == str(bs.spec)


def test_no_order_game(db_session, client):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    url_tpl = '/v1/group/games/{}'
    resp = client.get(url_tpl.format(game.id))
    assert not resp.json['users']


def test_create_order(db_session, client, user):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    client.login(user)
    url = '/v1/group/orders/'
    address = AddressDictFactory()
    data = dict(
        game_id=game.id,
        email='a@b.com',
        **address
    )

    resp = client.post(url, data=data)
    assert resp.status_code == 200, resp.json
    order = Order.query.first()

    assert order.batch_id == batch.id
    _assert_order_schema(resp.json, order)
    # no payment info yet
    assert resp.json['payment'] is None
    assert resp.json['spec'] == ''

    # add spec and quantity
    data.update(dict(spec='sss', quantity=2))
    user = UserFactory()
    client.login(user)
    resp = client.post(url, data=data)
    assert resp.json['spec'] == data['spec']

    # order amount should include both the price and shipping fee
    order = Order.query.filter(Order.user_id == user.id).first()
    assert order.amount == (
        batch.price * data['quantity'] + batch.shipping_price)
    assert order.currency == game.currency

    # there's no need to return game info here
    assert 'game' not in resp.json

    # it should fail if user tries to create another order in the same game
    resp = client.post(url, data=data)
    assert resp.status_code == 409, resp.json
    assert 'ORDER_EXISTS' == resp.json['message']

    # should not be able to create order in a finished batch
    game2 = batch.create_game()
    batch.end_at = arrow.utcnow().shift(minutes=-1)
    db_session.commit()
    data['game_id'] = game2.id
    resp = client.post(url, data=data)
    assert resp.status_code == 409
    assert 'BATCH_FINISHED' in resp.json['message']


def test_create_order_schema():
    # should validate email address format
    schema = OrderCreateSchema(strict=False)
    result = schema.load(dict(
        game_id=1,
        email='invalid email address',
        **AddressDictFactory()
    ))
    assert 'email' in result.errors
    # all fields should be required except spec
    for field in schema.fields.values():
        if field.name not in ['spec', 'quantity']:
            assert field.required


def test_orders_list(db_session, client):
    """
    两个用户分别在两个期次中创建了一个订单
    """
    batch = BatchFactory(total_shares=2)
    game = batch.create_game()
    db_session.flush()
    users = UserFactory.create_batch(2)
    for user in users:
        o = OrderFactory(user=user, game=game)
        payment = PaymentFactory(object=o, user=user)
        payment_signals.payment_created.send(payment)
        payment_signals.payment_succeeded.send(payment)
    game = batch.get_latest_game()
    for user in users:
        o = OrderFactory(user=user, game=game)
    db_session.commit()

    user = users[0]
    client.login(user)
    resp = client.get('/v1/group/orders/')
    # should only see my own orders
    orders = [Order.query.get(o['id']) for o in resp.json['objects']]
    for o in orders:
        assert o.user_id == user.id
    assert len(orders) == 2
    # list order
    assert_sorted_by(resp.json['objects'], '-created_at')
    # order schema
    # let's examine the order with payment
    order = [o for o in orders if o.payment][0]
    data = [o for o in resp.json['objects'] if o['id'] == order.id][0]
    payment = order.payment
    _assert_order_schema(data, order)
    # once payment is created, there should be payment info
    assert_dict_like(data['payment'], dict(
        id=payment.id,
        method=payment.method,
        amount=float(payment.amount),
        currency=dict(code=payment.currency.code),
        status=payment.status.name,
        vendor=payment.vendor.name,
        ref_id=payment.ref_id,
        payment_url=payment.payment_url,
    ))
    # order should carry game info too
    _assert_game_schema(data['game'], order.game)
    # create order with spec
    user = UserFactory()
    order = OrderFactory(user=user, game=game, spec='size:L', quantity=3)
    client.login(user)
    resp = client.get('/v1/group/orders/')
    assert resp.status_code == 200
    data = [o for o in resp.json['objects'] if o['id'] == order.id][0]
    assert data['spec'] == order.spec
    assert data['quantity'] == order.quantity


def test_games_sort(db_session, client, user):
    # 2 games in each country
    for weight in range(10):
        b = BatchFactory(sort_weight=weight)
        b.create_game()
    db_session.commit()
    url = '/v1/group/games/'
    resp = client.get(url)
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 10
    # sort order
    assert_sorted_by(
        resp.json['objects'],
        key=lambda o: (o['sort_weight'], o['product']['id'], ),
        reverse=True
    )


def test_category_games_api(db_session, client, user):
    #  games in different category
    category_ids = []
    for _ in range(5):
        b = BatchFactory()
        b.create_game()
        category_ids.append(b.category_id)
    db_session.commit()
    assert len(category_ids) == 5
    url = '/v1/group/games/'
    for category_id in category_ids:
        resp = client.get(url, query_string=dict(category_id=category_id))
        assert resp.status_code == 200
        assert len(resp.json['objects']) == 1
        assert resp.json['objects'][0]['category_id'] == category_id


def test_category_api(db_session, client):
    for weight in range(3):
        CategoryFactory(sort_weight=weight)
    db_session.flush()
    url = '/v1/group/categories/'
    resp = client.get(url)
    assert resp.status_code == 200
    assert len(resp.json['objects']) == 3
    assert_sorted_by(resp.json['objects'], '-sort_weight')
