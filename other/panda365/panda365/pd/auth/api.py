import arrow
from datadog import statsd
from facebook import GraphAPIError
from flask import Blueprint, current_app
from marshmallow.fields import Str
from pd.api import abort_json, io_annotated
from pd.ext import graph_factory
from pd.facebook.models import User
from pd.sqla import db
from .jwt import create_token as create_jwt_token, auth_required, current_user


auth = Blueprint('auth', __name__, url_prefix='/v1/auth')


token_schema = dict(jwt_token=Str(
    description='''
    Token decode后的payload:

        {
            "id": 10,  # user id
            "name": "John",  # user name
            "icon": "image url",
            "exp": 123123142  # token过期时间戳(unix timestamp)
        }

    ''')
)


@auth.route('/tokens/', methods=('POST',))
@io_annotated
def create_token(
    fb_token: Str(required=True, description='facebook access token')
) -> token_schema:
    """
    使用facebook access_token来获取API的token.
    """
    graph = graph_factory(fb_token)
    try:
        profile = graph.get_object('me')
        # profile has at least 2 fields: id and name
        user = User.fb_query(profile['id']).first()
        if not user:
            user = User(fb_id=profile['id'])
            statsd.increment('auth.registration')
            db.session.add(user)
        user.access_token = fb_token
        user.name = profile['name']
        # todo: other fields in profile

        if user.token_expire_soon():
            # extend token
            result = graph.extend_access_token(
                current_app.config['FACEBOOK_APP_ID'],
                current_app.config['FACEBOOK_APP_SECRET'],
            )
            user.access_token = result['access_token']
            # long-term access-token has a expiracy of 60 days
            user.access_token_expire_at = arrow.utcnow().replace(
                seconds=result.get('expires_in', 60 * 86400))
    except GraphAPIError as e:
        abort_json(403, e.message)
    db.session.flush()
    resp = dict(jwt_token=create_jwt_token(user))
    db.session.commit()
    return resp


@auth.route('/tokens/refresh/', methods=('POST',))
@io_annotated
@auth_required
def extend_token() -> token_schema:
    """
    使用现有的API token来获取有效期更长的token.
    """
    return dict(jwt_token=create_jwt_token(current_user))
