from flask import Blueprint, abort, render_template

from pd.constants import Country
from pd.groupon.models import Game, Batch, Order, OrderStatus
from pd.groupon.schema import ProductSchema

share = Blueprint(
    'groupon_pages', __name__,
    template_folder='templates',
)


@share.route('/<string:country>/groupon/<int:id>.html')
def game(country, id):
    try:
        country = Country(country.upper())
    except ValueError:
        abort(404)

    """
        团购商品列表
        """
    game = Game.query.join(Batch).filter(
        Game.batch_id == id,
        # Game.is_running,
        Game.country == country,
    ).first()

    if not game:
        abort(404)

    orders = Order.query.filter(
        Order.status.in_([
            OrderStatus.paid, OrderStatus.processing, OrderStatus.shipped]),
        Order.game_id == game.id
    ).all()

    # if not orders:
    #     abort(404)
    schema = ProductSchema()
    product_dict = schema.dump(game.product).data
    return render_template(
        'new_detail.html',
        game=game,
        product_info=product_dict['info'],
        orders=orders
    )


@share.route('/htp.html')
def htp():
    return render_template('htp.html')
