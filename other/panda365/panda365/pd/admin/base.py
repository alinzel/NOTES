from flask import redirect, request, url_for
from flask_babelex import Locale
from flask_admin import AdminIndexView as _AdminIndexView, expose
from flask_admin.form.fields import Select2Field
from flask_admin.contrib.sqla import ModelView as _ModelView
from flask_admin.contrib.sqla.form import (
    converts,
    AdminModelConverter as BaseModelConverter,
)
from flask_security import current_user
from flask_wtf import FlaskForm
from .format import COLUMN_TYPE_FORMATTERS
from wtforms.validators import InputRequired


class SecureForm(FlaskForm):

    def __init__(self, formdata=None, obj=None, **kwargs):
        """
        A workaround concerning sqlalchemy unique constraint
        refs: https://github.com/flask-admin/flask-admin/issues/486
        """
        self._obj = obj
        super().__init__(formdata=formdata, obj=obj, **kwargs)


class AdminModelConverter(BaseModelConverter):

    @converts('ArrowType')
    def convert_arrow(self, field_args, **extra):
        from .fields import ArrowField
        return ArrowField(**field_args)

    _locale_en = Locale('en')
    _currency_choices = sorted(
        ((code, '{}: {}'.format(code, desc))
         for code, desc in _locale_en.currencies.items()),
        key=lambda r: r[0]
    )

    @converts('CurrencyType')
    def convert_currency(self, field_args, **extra):
        field_args['choices'] = self._currency_choices
        field_args['default'] = 'USD'
        return Select2Field(**field_args)

    @converts('ChoiceType')
    def convert_enum(self, field_args, **extra):
        from .fields import EnumField
        col = extra['column']
        return EnumField(enum=col.type.choices, **field_args)


class SecurityMixin:

    def has_roles(self, roles):
        return current_user.has_role(roles)

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class ModelView(SecurityMixin, _ModelView):
    can_create = False
    can_delete = False
    can_view_details = True

    column_type_formatters = COLUMN_TYPE_FORMATTERS

    form_base_class = SecureForm
    model_form_converter = AdminModelConverter
    named_filter_urls = True
    disabled_fields_on_edit_form = ()

    def _remove_validator(self, validators, validator_cls):
        return [v for v in validators if not isinstance(v, validator_cls)]

    def edit_form(self, obj=None):
        # 这些字段被disable了，它们不会被POST到edit_view
        # 因此需要去除它们的required验证
        form = super().edit_form(obj)
        if self.disabled_fields_on_edit_form:
            for k in self.disabled_fields_on_edit_form:
                field = getattr(form, k)
                field.validators = self._remove_validator(
                    field.validators, InputRequired)
        return form


class AdminIndexView(SecurityMixin, _AdminIndexView):

    @expose()
    def index(self):
        from pd.facebook.models import Country
        self._template_args['countries'] = Country
        return self.render(self._template)
