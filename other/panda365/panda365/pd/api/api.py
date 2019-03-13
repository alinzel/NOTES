from collections import OrderedDict
import markdown as md
from marshmallow import Schema
from marshmallow.fields import Nested, List
from marshmallow.validate import Length, OneOf
from flask import Blueprint, current_app, jsonify, render_template


api = Blueprint(
    'api', __name__,
    url_prefix='/v1',
    template_folder='templates',
)

_default_methods = {'HEAD', 'OPTIONS'}


def _clean_desc(desc, markdown=True):
    lines = []
    for line in desc.split('\n'):
        if line.startswith('    '):
            line = line[4:]
        lines.append(line)
    desc = '\n'.join(lines)
    if markdown:
        desc = md.markdown(desc, output_format='html5')
    return desc


_doc_topics = [{
    'topic': '多语言',
    'id': 'i18n',
    'desc': _clean_desc('''
API返回值的某些字段支持多语言，例如`post.message`. 要控制返回语言的类型，传入
HTTP header `Accept-Language`. 如果这个header没有设置，或设置的语言服务器暂未
支持，则将返回服务器默认语言，通常是英语. 例如，要获取简体中文内容:
`Accept-Language: zh-cn`.
''')
}, {
    'topic': '图片尺寸',
    'id': 'image-dimension',
    'desc': _clean_desc('''
图片链接中包含了图片的尺寸信息。 例如:
`https://example.org/image_100_150.png`. 客户端不能认为所有图片都有尺寸
信息；旧数据(2017-06-01以前)没有尺寸信息。
''')
}]


def _parse_field(field):
    ret = {}
    attrs = []
    container = None
    if isinstance(field, List):
        # ret['type'] = 'List of {}'.format(field.container.__class__.__name__)
        # container = field.container
        container = _parse_field(field.container)
        container['attrs'] = ', '.join(
            item for item in container['attrs']
            if not item.startswith('location'))
        ret['type'] = 'List of {type}[{attrs}]'.format(**container)
    else:
        ret['type'] = field.__class__.__name__
    if field.required:
        attrs.append('required')
    if field.default:
        attrs.append(
            'default={}'.format(repr(field.default)))  # pragma: no cover
    locations = field.metadata.get('locations')
    if locations:
        locations = '({})'.format(', '.join(
            l if l != 'view_args' else 'path' for l in locations))
    else:
        locations = field.metadata.get('location', 'json')
        if locations == 'view_args':
            locations = 'path'
    attrs.append('location={}'.format(locations))
    # if container:
    #     field = container
    if isinstance(field.validate, list):
        for v in field.validate:
            if isinstance(v, Length):  # pragma: no cover
                if v.min:
                    attrs.append('min_length={}'.format(v.min))
                if v.max:
                    attrs.append('max_length={}'.format(v.max))
            if isinstance(v, OneOf):
                attrs.append(
                    'one of ({})'.format(
                        ','.join(field._serialize(c, None, None)
                                 for c in v.choices)))
    ret['attrs'] = attrs
    desc = field.metadata.get('description')
    if desc:
        ret['desc'] = _clean_desc(desc)
    if isinstance(field, Nested):
        ret['fields'] = {
            name: _parse_field(f) for name, f in field.schema.fields.items()}
    return ret


def extract_docs(view_func, markdown=False):
    docs = dict(desc={}, headers={}, params={}, returns={})
    # description
    if view_func.__doc__:
        docs['desc'] = _clean_desc(view_func.__doc__, markdown)
    # input arguments
    input_schema = getattr(view_func, '_input_schema', None)
    if input_schema:
        if isinstance(input_schema, Schema):
            params = (
                (name, _parse_field(f))
                for name, f in input_schema.fields.items()
            )
        else:
            params = (
                (name, _parse_field(field))
                for name, field in input_schema.items()
            )
        docs['params'] = OrderedDict(params)
    # returns
    output_schema = getattr(view_func, '_output_schema', None)
    if output_schema:
        docs['returns'] = dict(
            model=output_schema.__class__.__name__.replace(
                'Schema', '') or 'Object',
            many=output_schema.many,
            fields=OrderedDict(
                (name, _parse_field(f))
                for name, f in output_schema.fields.items()
            )
        )
    # headers
    if getattr(view_func, '_auth_required', False):
        docs['headers']['Authorization'] = {
            'desc': 'Bearer {jwt token}',
            'attrs': ['required'],
        }
    if getattr(view_func, '_auth_optional', False):
        docs['headers']['Authorization'] = {
            'desc': 'Bearer {jwt token}',
            'attrs': ['optional'],
        }
    return docs


def get_endpoints(url_external=True, markdown=False):
    scheme = current_app.config['PREFERRED_URL_SCHEME']
    server = current_app.config['SERVER']
    return sorted([{
        'endpoint': rule.endpoint,
        'rule': ('{}://{}{}'.format(scheme, server, rule.rule)
                 if url_external else rule.rule),
        'methods': list(rule.methods - _default_methods),
        'docs': extract_docs(
            current_app.view_functions.get(rule.endpoint),
            markdown,
        )
    } for rule in current_app.url_map.iter_rules()
        if rule.rule.startswith('/v1')],
        key=lambda r: (r['rule'], r['methods']),
    )


@api.route('/')
def index():
    '''
    API文档
    '''
    return jsonify(
        topics=_doc_topics,
        endpoints=[dict(
            endpoint=ep['endpoint'],
            rule=ep['rule'],
            methods=ep['methods'],
            description=ep['docs']['desc']
        ) for ep in get_endpoints()],
        docs_url='{}://{}/v1/docs.html'.format(
            current_app.config['PREFERRED_URL_SCHEME'],
            current_app.config['SERVER'],
        ),
    )


@api.route('/docs.html')
def docs():
    return render_template(
        'api/docs.html',
        topics=_doc_topics,
        endpoints=get_endpoints(False, True),
    )
