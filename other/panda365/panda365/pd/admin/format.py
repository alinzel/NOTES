from enum import Enum
from arrow import Arrow
from flask import Markup, render_template_string, url_for
from flask_babelex import get_locale
from pd.i18n import get_timezone


def format_imgs(*urls):
    return Markup(render_template_string(
        '''
        <div style="min-width: 120px">
        {% for url in urls %}
        <a href="{{ url }}" target="_blank">
        <img style="object-fit: cover; width: 120px; max-height: 180px"
           class="img-thumbnail" src="{{ url }}" alt="{{ url }}"
           title="{{ url }}">
        </a>
        {% endfor %}
        </div>
        ''', urls=urls)
    )


def format_progress(current, total, text=None):
    progress = 100 * current / total
    return Markup(render_template_string(
        '''
        <div style="text-align: center">
            <h5>{{'{:.2f}'.format(progress)}}%</h5>
            <div>
              {% if text %}
                {{ text | safe }}
              {% else %}
                ({{current}}/{{total}})
              {% endif %}
            </div>
            <div class="progress">
                <div class="progress-bar" style="width: {{progress}}%"></div>
            </div>
        </div>
        ''', current=current, total=total, progress=progress, text=text))


def format_link(url, text='', title='', target=''):
    return Markup(
        '<a class="btn btn-default btn-xs" href="{url}" title="{title}" '
        'target="{target}">{text}</a>'.format(
            url=url, text=text, title=title, target=target,
        ))


def format_links(*links):
    if links:
        return Markup(' '.join(links))


def model_detail_link(model_name, id):
    return format_link(
        url_for(
            '{}.details_view'.format(model_name.lower()),
            id=id
        ),
        text='{}[{}]'.format(model_name, id),
    )


def model_list_link(model_name, text=None, endpoint=None, **kwargs):
    return format_link(
        url_for(
            '{}.index_view'.format(endpoint or model_name.lower()), **kwargs),
        text=text or '{}s'.format(model_name),
    )


def trans_hybrid_formatter(view, ctx, model, name):
    value = getattr(model, name)
    if value:
        return Markup(''.join(
            '<p><span class="badge">{}</span> {}</p>'.format(lang, trans)
            for lang, trans in getattr(model, name).items())
        )
    return ''


def trans_hybrid_product_info_formatter(view, ctx, model, name):
    value = getattr(model, name)
    if value:
        return Markup(render_template_string('''
        <div>
        {% for lang, content in trans.items() %}
        <div>
            <div class="badge">{{lang}}</div>
            <table class="table table-bordered table-condensed table-hover">
                {% for line in content.split('\n') %}
                    {% set k, v = line.split(':') %}
                    <tr>
                        <td><b>{{ k }}</b></td>
                        <td>{{ v }}</td>
                    </tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        </div>
        ''', trans=value))


def arrow_formatter(view, value):
    l = get_locale()
    try:
        content = value.humanize(
            locale='{}_{}'.format(l.language, l.territory).lower())
    except ValueError:
        content = value.humanize()
    return Markup('<span title="{}">{}</span>'.format(
        value.to(get_timezone()).format(), content
    ))


def enum_formatter(view, value):
    if hasattr(value, 'admin_label'):
        txt = value.admin_label
    elif hasattr(value, 'label'):
        txt = value.label
    else:
        txt = value.name
    return Markup('<span class="label label-primary">{}</span>'.format(txt))


COLUMN_TYPE_FORMATTERS = {
    Arrow: arrow_formatter,
    Enum: enum_formatter,
}
