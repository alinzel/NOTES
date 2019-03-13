from flask import Blueprint
from sqlalchemy_utils import sort_query

api = Blueprint('facebook', __name__, url_prefix='/v1')


def reverse_created_at(query):
    return sort_query(query, '-created_at')


from .posts import *  # noqa
from .comments import *  # noqa
from .likes import *  # noqa
