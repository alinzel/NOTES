from facebook import get_user_from_cookie
from flask import Blueprint, abort, current_app, render_template, request
from webargs import fields
from webargs.flaskparser import use_args
from .schema import FBUpdateSchema
from .parser import parse_update


facebook = Blueprint(
    'fb', __name__,
    url_prefix='/facebook',
    template_folder='templates',
)


@facebook.route('/')
@use_args({
    'hub.mode': fields.String(required=True),
    'hub.challenge': fields.String(required=True),
    'hub.verify_token': fields.String(required=True),
})
def callback_verify(args):
    hub = args['hub']
    if (hub['mode'] == 'subscribe' and
            hub['verify_token'] == current_app.config[
                'FACEBOOK_VERIFY_TOKEN']):
        return hub['challenge']
    abort(422)


@facebook.route('/', methods=('POST',))
@use_args(FBUpdateSchema(), locations=('json', 'headers'))
def callback(args):
    """
    Example payload::

        {
            "entry": [{
                "changes": [{
                    "field": "feed",
                    "value": {
                            "item": "status",
                            "sender_name": "Panda365",
                            "sender_id": 286247441793403,
                            "post_id": "286247441793403_288731331545014",
                            "verb": "add",
                            "published": 1,
                            "created_time": 1489996742,
                            "message": "test post without a photo"
                            }
                }],
                "id": "286247441793403",
                "time": 1489996743
            }],
            "object": "page"
        }

    This view should parse the changes and fire the corresponding signals
    """
    parse_update(args)
    return '', 200


@facebook.route('/_auth_demo.html')
def auth_demo():
    user = get_user_from_cookie(
        cookies=request.cookies,
        app_id=current_app.config['FACEBOOK_APP_ID'],
        app_secret=current_app.config['FACEBOOK_APP_SECRET'],
    )
    return render_template(
        'facebook/_auth.jinja2',
        user=user,
    )
