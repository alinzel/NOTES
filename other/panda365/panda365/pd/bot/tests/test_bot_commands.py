from blinker import signal
from pd.bot.commands import create_bot, update_game_left_share
from pd.groupon.factory import UserFactory, BatchFactory, OrderFactory
from pd.payment.factory import PaymentFactory
from pd.groupon.models import Order


def test_create_bot(app_context):
    from pd.facebook.schema import UserSchema

    bot = create_bot('blah', 'helms')
    assert bot.is_bot
    assert bot.name == 'helms'

    dumped = UserSchema().dump(bot).data
    assert dumped['name'] == 'helms'


def test_update_game_left_share(db_session):
    user = UserFactory()
    batch = BatchFactory(total_shares=5)
    for _ in range(10):
        UserFactory(is_bot=True)
    game = batch.create_game()
    db_session.flush()
    order = OrderFactory(game=game, user=user)
    game.left_shares = 3
    db_session.commit()
    update_game_left_share()
    orders = Order.query.filter(Order.game == game).all()
    bot_user = 0
    for o in orders:
        if o.user.is_bot:
            bot_user += 1
    assert len(orders) == 3, bot_user == 2
    payment = PaymentFactory(object=order, user=order.user)
    signal('payment_created').send(payment)
    signal('payment_succeeded').send(payment)
    db_session.commit()
    assert len(game.users) == 3

    batch = BatchFactory(total_shares=5)
    game = batch.create_game()
    update_game_left_share()
    assert not game.users
