from pd.groupon.factory import BatchFactory, UserFactory, OrderFactory
from sqlalchemy import desc
from pd.groupon.models import Game, Order


def test_groupon_progress(db_session):
    for i in range(2):
        b = BatchFactory()
        g = b.create_game()
        g.left_shares = i
        db_session.commit()

    games = Game.query.order_by(Game.groupon_progress).all()
    assert games[0].groupon_progress < games[1].groupon_progress

    games = Game.query.order_by(desc(Game.groupon_progress)).all()
    assert games[0].groupon_progress > games[1].groupon_progress


def test_check_left_shares(db_session):
    user = UserFactory()
    batch = BatchFactory(total_shares=5)
    for _ in range(10):
        UserFactory(is_bot=True)
    game = batch.create_game()
    db_session.flush()
    OrderFactory(game=game, user=user)
    game.left_shares = 1
    db_session.commit()
    game.check_left_shares()
    orders = Order.query.filter(Order.game == game).all()
    bot_user = 0
    for o in orders:
        if o.user.is_bot:
            bot_user += 1
    # user order status is not paid
    assert len(orders) == 5, bot_user == 4
