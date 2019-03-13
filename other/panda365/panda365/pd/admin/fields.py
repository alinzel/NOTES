import mimetypes
import os
import uuid

import arrow
from flask import current_app
from flask_admin.form import BaseForm, FileUploadInput, ImageUploadInput
from flask_admin.form.fields import DateTimeField, Select2Field
from flask_admin.model.fields import InlineFormField, InlineFieldList
from flask_babelex import lazy_gettext, gettext as _
from werkzeug.datastructures import FileStorage
from wtforms import fields, validators, ValidationError
from wtforms.utils import unset_value
from wtforms.widgets import html_params, HTMLString
from PIL import Image

from pd.i18n import get_timezone
from pd.ext import s3ext


class ArrowField(DateTimeField):

    def __init__(self, label=None, validators=None,
                 format='YYYY-MM-DD HH:mm:ss', **kwargs):
        super().__init__(label, validators, format, **kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            if self.data:
                return self.data.to(get_timezone()).format(self.format)
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist)
            try:
                self.data = arrow.get(
                    date_str, self.format, tzinfo=get_timezone()
                ).to('utc')
            except arrow.parser.ParserError:
                self.data = None
                raise ValueError(self.gettext('Not a valid datetime value'))


class EnumField(Select2Field):

    def __init__(self, enum, **kwargs):
        self.enum = enum
        value_type = type(list(enum)[0].value)

        def coerce(v):
            if isinstance(v, enum):
                return v
            return enum(value_type(v))

        super().__init__(
            coerce=coerce,
            choices=[
                (item, getattr(item, 'admin_label', item.name))
                for item in enum
            ],
            **kwargs)

    def process_data(self, value):
        if value:
            value = value.value
        return super().process_data(value)

    def iter_choices(self):
        for value, label, selected in super().iter_choices():
            if value != '__None':
                value = value.value
            yield value, label, selected


class HybridTranslationForm(BaseForm):
    locale = Select2Field(lazy_gettext('locale'))
    content = fields.TextAreaField(
        lazy_gettext('content'), validators=[validators.DataRequired()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.locale.choices = [
            (locale, locale) for locale in current_app.config[
                'BABEL_SUPPORTED_LOCALES']]


class HybridTranslationField(InlineFieldList):
    inline_form = HybridTranslationForm

    def __init__(self, min_entries=0, **field_args):
        v = field_args.setdefault('validators', [])
        # flask-admin would add those validators to a field based on
        # if the field if nullable
        # however, for a FieldList, those validators makes no sense.
        # here we remove them
        field_args['validators'] = v[1:]
        field_args['validators'].append(self.validate_locales)
        super().__init__(
            InlineFormField(self.inline_form), min_entries=min_entries,
            **field_args)

    def validate_locales(self, form, field):
        locales = [entry.data['locale'] for entry in field.entries]
        if len(set(locales)) != len(locales):
            raise ValidationError(
                _('translation for each locale can only be given once'))

    def process(self, formdata, data=unset_value):
        if data:  # pragma: no cover
            data = [dict(locale=locale, content=content)
                    for locale, content in data.items()]
        super().process(formdata, data)

    def populate_obj(self, obj, name):
        trans = {}
        for field in self.entries:
            trans[field.data['locale']] = field.data['content']
        setattr(obj, name, trans)


def get_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()


def default_namegen(obj, file_data):
    """
    by default uses uuid to avoid name collisions
    """
    name = uuid.uuid4().hex
    ext = get_extension(file_data.filename)
    if ext:
        name = '{}.{}'.format(name, ext)
    return name


class S3FileUploadField(fields.StringField):
    widget = FileUploadInput()

    def __init__(
        self, s3_directory='files',
        namegen=None,
        allowed_extensions=None,
        allow_overwrite=False,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.s3_directory = s3_directory
        self.allowed_extensions = allowed_extensions
        self.namegen = namegen or default_namegen
        self._allow_overwrite = allow_overwrite
        self._should_delete = False

    def is_file_allowed(self, filename):
        """
            Check if file extension is allowed.

            :param filename:
                File name to check
        """
        if not self.allowed_extensions:
            return True

        return ('.' in filename and
                get_extension(filename) in
                map(lambda x: x.lower(), self.allowed_extensions))

    def _is_uploaded_file(self, data):
        return data and isinstance(data, FileStorage) and data.filename

    def pre_validate(self, form):
        if (self._is_uploaded_file(self.data) and
                not self.is_file_allowed(self.data.filename)):
            raise ValidationError('Invalid file extension')

    def process(self, formdata, data=unset_value):
        if formdata:
            marker = '_%s-delete' % self.name
            if marker in formdata:
                self._should_delete = True

        return super().process(formdata, data)

    def process_formdata(self, valuelist):
        if self._should_delete:
            self.data = None
        elif valuelist:
            for data in valuelist:
                if self._is_uploaded_file(data):
                    self.data = data
                    self.path = self._get_path(data.filename)
                    break

    def populate_obj(self, obj, name):
        field = getattr(obj, name, None)
        if field and self._should_delete:
            self._delete_file(field)
            setattr(obj, name, None)
            return

        if self._is_uploaded_file(self.data):
            # replace old file
            if field:
                self._delete_file(field)

            filename = self.namegen(obj, self.data)
            # new path
            path = self._save_file(self.data, filename)
            # update filename of FileStorage to our validated name
            self.data.filename = path

            setattr(obj, name,
                    'https://{}/{}'.format(s3ext.store.bucket_name, path))

    def _get_path(self, filename):
        return os.path.join(self.s3_directory, filename)

    def _file_exists(self, filename):
        return s3ext.store.path_exists(self._get_path(filename))

    def _delete_file(self, path):
        s3ext.store.delete_file(path)

    def _save_file(self, data, filename):
        path = self._get_path(filename)

        if (not self._allow_overwrite and
                self._file_exists(filename)):  # pragma: no cover
            raise ValueError('File "{}" already exists.'.format(path))

        s3ext.store.save_file(path, data)
        return path


class S3ImageUploadInput(ImageUploadInput):

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)

        args = {
            'file': html_params(type='file',
                                **kwargs),
            'text': html_params(type='text',
                                readonly='readonly',
                                value=field.data or '',
                                name=field.name),
            'marker': '_%s-delete' % field.name
        }

        if field.data:
            args['image'] = html_params(src=field.data)

            template = self.data_template
        else:
            template = self.empty_template

        return HTMLString(template % args)

    def get_url(self, field):  # pragma: no cover
        return field.data


def gen_image_name(obj, file_data):
    """
    by default uses uuid to avoid name collisions, also adds image dimension
    to the name: "`{uuid}_{width}_{height}`.jpg"
    """
    parts = [uuid.uuid4().hex]
    content_type, _ = mimetypes.guess_type(file_data.filename)
    if content_type and content_type.startswith('image'):  # pragma: no cover
        im = Image.open(file_data)
        parts.append('_{}_{}'.format(im.width, im.height))
        file_data.seek(0)
    ext = get_extension(file_data.filename)
    if ext:  # pragma: no cover
        parts.append('.' + ext)
    return ''.join(parts)


class S3ImageUploadField(S3FileUploadField):
    widget = S3ImageUploadInput()

    def __init__(self, *args, s3_directory='images', **kwargs):
        kwargs['namegen'] = gen_image_name
        super().__init__(*args, s3_directory=s3_directory, **kwargs)


class ProductInfoField(fields.TextAreaField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            'description',
            '每行一条，名称和内容以英文冒号":"分割。例如: "Brand: Apple"。'
            '名称和内容中均不能包含":"。'
        )
        super().__init__(*args, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            parts = []
            try:
                for line in valuelist[0].split('\n'):
                    k, v = line.split(':')
                    parts.append('{}:{}'.format(
                        k.strip(),
                        v.strip(),
                    ))
            except ValueError:
                raise ValidationError('"{}"不符合格式要求'.format(line))
            valuelist = ['\n'.join(parts)]
        super().process_formdata(valuelist)


class ProductInfoTranslationForm(HybridTranslationForm):
    content = ProductInfoField(
        lazy_gettext('content'), validators=[validators.DataRequired()])


class ProductInfoTranslationField(HybridTranslationField):
    inline_form = ProductInfoTranslationForm
