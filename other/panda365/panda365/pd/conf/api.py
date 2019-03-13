from flask import Blueprint
from marshmallow import fields
from pd.api import abort_json, io_annotated
from .schema import ConfSchema
from .models import Conf


api = Blueprint('conf_api', __name__, url_prefix='/v1/conf')


@api.route('/<name>')
@io_annotated
def conf_get(
    name: fields.Str(required=True, location='view_args')
) -> ConfSchema():
    """
    根据名字返回客户端配置
    """
    conf = Conf.query.filter(Conf.name == name).first()
    if not conf:
        abort_json(404)
    return conf
