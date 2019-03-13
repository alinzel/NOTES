from flask import Blueprint, current_app


bp = Blueprint(
    'www', __name__,
)


@bp.route('/')
def home():
    return current_app.send_static_file('index.html')


@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')
