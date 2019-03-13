from io import BytesIO
import re
import uuid

import pytest
from werkzeug.datastructures import FileStorage, MultiDict
from wtforms import Form

from pd.admin.fields import (
    S3FileUploadField, S3ImageUploadField, S3ImageUploadInput
)


pytestmark = pytest.mark.usefixtures('s3_storage_mock')


class Foo:
    txt_file = None


class UploadForm(Form):
    txt_file = S3FileUploadField()


formdata = MultiDict({
    'txt_file': FileStorage(stream=BytesIO(b'123'), filename='test.txt')
})


def test_upload_file(app, s3_storage_mock):
    form = UploadForm(formdata=formdata)
    assert form.validate()
    foo = Foo()
    form.populate_obj(foo)
    assert foo.txt_file.startswith(
        'https://{}/files'.format(app.config['S3_BUCKET']))
    name = foo.txt_file.split('/')[-1]
    uuid_part = name.split('.')[0]
    # name should be a uuid
    uuid.UUID(uuid_part)
    assert s3_storage_mock.save_file.called

    # replace file
    form2 = UploadForm(formdata=formdata)
    assert form2.validate()
    form2.populate_obj(foo)
    assert name not in foo.txt_file


@pytest.mark.parametrize('data', [
    {'txt_file': None},
    {'txt_file': 'test'},
    {'blah': 'hey'},
])
def test_upload_non_files(data):
    foo = Foo()

    form = UploadForm(formdata=MultiDict(data))
    assert form.validate()
    form.populate_obj(foo)
    assert not foo.txt_file


def test_delete_file(s3_storage_mock):
    foo = Foo()
    pdf_url = '//static.test.com/test.pdf'
    foo.txt_file = pdf_url
    form = UploadForm(formdata=MultiDict({
        '_txt_file-delete': '1'
    }), obj=foo)
    assert form.validate()
    form.populate_obj(foo)
    assert not foo.txt_file
    assert s3_storage_mock.delete_file.called
    assert s3_storage_mock.delete_file.call_args[0][0] == pdf_url


@pytest.mark.parametrize('filename,allowed_extensions,success', [
    # given a txt file:
    ['test.txt', ('jpg', 'png'), False],  # txt not allowed
    ['test.txt', ('jpg', 'txt'), True],  # txt allowed
    ['test.txt', None, True],  # extension not limited
    ['test.txt', ('jpg', 'TXT'), True],  # extension should be case insensitive
    # given a file without extension
    ['test', ('jpg', 'png'), False],  # "no extension" is not in allowed
    ['test', None, True],  # extension unlimited, any type can be uploaded
])
def test_allowed_extensions(filename, allowed_extensions, success):
    class UploadForm(Form):
        txt_file = S3FileUploadField(allowed_extensions=allowed_extensions)
    form = UploadForm(MultiDict({
        'txt_file': FileStorage(stream=BytesIO(b'123'), filename=filename)
    }))
    assert form.validate() == success, form.errors
    form.populate_obj(Foo())
    if not success:
        assert 'Invalid file extension' in str(form.errors['txt_file'])


class ImageUploadForm(Form):
    image = S3ImageUploadField()


class Bar:
    image = None


def _get_image_form(image_file):
    return ImageUploadForm(formdata=MultiDict({
        'image': FileStorage(
            stream=image_file,
            filename='test.png',
        )
    }))


def test_upload_image(app, s3_storage_mock, png_path):
    bar = Bar()
    with open(png_path, 'rb') as im_file:
        form = _get_image_form(im_file)
        form.populate_obj(bar)
        # dimension of the png image is (4, 3)
        # it should be available via the url
        path = bar.image.split('/')[-1]
        match = re.match('(\w+)_(?P<width>\d+)_(?P<height>\d+)', path)
        assert match and match.groupdict() == dict(width='4', height='3')


def test_image_field_widget(s3_storage_mock, png_path):
    form = ImageUploadForm()
    assert isinstance(form.image.widget, S3ImageUploadInput)
    # should render a file input if no field data is given
    assert form.image() == '<input id="image" name="image" type="file">'
    # should render image otherwise
    bar = Bar()
    with open(png_path, 'rb') as im_file:
        form = _get_image_form(im_file)
        form.populate_obj(bar)
        new_form = ImageUploadForm(obj=bar)
        assert re.search('img src="(.*)"> <input', new_form.image())
