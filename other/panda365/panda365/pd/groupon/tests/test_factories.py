import pytest
from pd.groupon.factory import (
    ProductFactory, SpecFactory, SpecOptionFactory, BatchFactory,
    BatchSpecFactory, OrderFactory,
)


pytestmark = pytest.mark.db


def test_simple_factories():
    # product
    product = ProductFactory()
    assert product.id
    assert product.media_urls
    assert product.description
    # spec
    SpecFactory()
    SpecOptionFactory()
    # batch
    batch = BatchFactory()
    assert batch.category


def test_batch_spec_factory(db_session):
    batch = BatchFactory()
    bs = BatchSpecFactory(batch_id=batch.id)
    assert not bs.options
    assert bs in batch.specs

    # options should be associated with the BatchSpec if given
    options = SpecOptionFactory.build_batch(2)
    bs = BatchSpecFactory(batch_id=batch.id, options=options)
    db_session.flush()
    assert bs.options
    assert bs.options[0].id


def test_order_factory(db_session):
    batch = BatchFactory()
    game = batch.create_game()
    db_session.commit()
    order = OrderFactory.build(game=game)
    assert order.full_name
    order = OrderFactory.build(game=game, full_name='john')
    assert order.full_name == 'john'
    # should set price, currency and batch if game is given
    for k in ('batch', 'price', 'currency', 'shipping_price'):
        assert getattr(order, k) == getattr(game, k)
    assert order.amount == game.price + game.shipping_price
    # otherwise it should not
    order = OrderFactory.build()
    for k in ('batch', 'price', 'currency', 'shipping_price'):
        assert getattr(order, k) is None
    assert order.amount is None
    assert order.spec
