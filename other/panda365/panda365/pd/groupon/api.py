from .models import Game, Order, Category, BatchSpec
from .schema import GameSchema, OrderSchema, OrderCreateSchema, CategorySchema
from flask import Blueprint
from pd.api import abort_json
from pd.api.fields import Enum
from pd.api.io import io_annotated
from pd.auth.jwt import auth_required, auth_optional, current_user_data
from pd.constants import Country
from pd.ext import limiter
from pd.sqla import db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy_utils import sort_query
from marshmallow.fields import Int


api = Blueprint('groupon_api', __name__, url_prefix='/v1/group')


@api.route('/games/')
@io_annotated
def games_list(
    country: Enum(Country, location='query'),
    category_id: Int(description='category id'),
) -> GameSchema(exclude=('sold_num', 'order'), many=True):
    """
    团购商品列表
    """
    q = Game.query.filter(
        Game.is_running,
    ).options(
        joinedload('product'),
        subqueryload('product.media'),
    ).join(Game.product)
    if country:
        q = q.filter(Game.country == country)
    if category_id:
        q = q.filter(Game.category_id == category_id)
    return sort_query(q, '-sort_weight', '-product-created_at')


@api.route('/games/<int:id>')
@auth_optional
@io_annotated
def game_detail(id) -> GameSchema():
    """
    商品详情

    此接口返回的期次信息与列表接口的不同:

    * 包含批次`sold_num`
    * 如果当前用户已登陆，返回用户在此期次的订单信息`order`

    """
    game = Game.query.options(db.joinedload(Game.batch)).get_or_404_json(id)
    orders = Order.query.filter(Order.game_id == game.id)
    if current_user_data:
        order = orders.filter(
            Order.user_id == current_user_data['id'],
        ).first()
    else:
        order = None
    game.order = order
    specs = BatchSpec.query.filter(BatchSpec.batch_id == game.batch.id)
    game.specs = specs
    return game


@api.route('/orders/', methods=('POST',))
@auth_required
@limiter.limit_and_check(
    # 预防double click
    '1/2 second',
    key_func=lambda: 'users/{}/orders'.format(  # pragma: no cover
        current_user_data['id'],
    )
)
@io_annotated
def order_create(
    **data: OrderCreateSchema()
) -> OrderSchema(exclude=('game',)):
    """
    订单创建接口.

    一个用户在一个期次至多参加一次。
    """
    game = Game.query.options(
        db.joinedload(Game.batch)
    ).get_or_404_json(data['game_id'])
    if not game.batch.is_running:
        abort_json(409, 'BATCH_FINISHED')
    order = Order(
        game=game,
        user_id=current_user_data['id'],
        **data
    )
    try:
        db.session.add(order)
        db.session.commit()
    except IntegrityError as e:
        if Order.UQ_USER_GAME in str(e):
            db.session.rollback()
            abort_json(409, 'ORDER_EXISTS')
        else:  # pragma: no cover
            raise
    return order


@api.route('/orders/')
@auth_required
@io_annotated
def orders_list() -> OrderSchema(many=True):
    """
    我的订单列表
    """
    return Order.query.filter(
        Order.user_id == current_user_data['id'],
    ).options(
        joinedload('game'),
        joinedload('game.product'),
        subqueryload('game.product.media'),
    ).order_by(db.desc(Order.created_at))


@api.route('/categories/')
@io_annotated
def categories_list() -> CategorySchema(many=True):
    """
    分类列表
    """
    return Category.query.order_by(db.desc(Category.sort_weight))
