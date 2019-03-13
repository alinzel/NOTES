from flask import Blueprint, abort, render_template, request
from sqlalchemy.orm import subqueryload, contains_eager
from pd.constants import Country
from .models import Wish, WishPrice


bp = Blueprint(
    'wish_pages', __name__,
    template_folder='templates',
)


@bp.route('/<string:country>/wishes/<int:id>.html')
def detail(country, id):
    try:
        country = Country(country.upper())
    except ValueError:
        abort(404)
    wish = Wish.query.join(WishPrice).filter(
        WishPrice.country == country,
        Wish.id == id,
    ).options(
        subqueryload('media'),
        contains_eager('prices'),
    ).first()
    if not wish:
        abort(404)
    return render_template(
        'wishes/detail.html',
        wish=wish,
        wish_price=wish.country_price,
        uid=request.args['uid'],
    )
