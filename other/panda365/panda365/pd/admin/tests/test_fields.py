from enum import Enum
import arrow
from werkzeug.datastructures import MultiDict
from wtforms import Form
from pd.admin.fields import ArrowField, EnumField, ProductInfoField


def test_arrow_field(app):

    class FooForm(Form):
        created_at = ArrowField()

    class Foo:

        def __init__(self, c):
            self.created_at = c

    t = arrow.get('2017-05-01 00:00:00+00')
    foo = Foo(t)

    with app.test_request_context('/admin/'):
        # displayed time is user's local time
        form = FooForm(obj=foo)
        assert form.created_at.data == t
        # should show local time
        assert form.created_at._value() == '2017-05-01 08:00:00'

        # users should be able to input their local time
        form = FooForm(formdata=MultiDict([
            ('created_at', '2017-05-02 18:00:00'),  # users input local time
        ]))
        assert form.validate()
        form.populate_obj(foo)
        # data should be utc
        assert foo.created_at == arrow.get('2017-05-02 10:00:00')

        # test formdata
        # empty input is ok
        form = FooForm(formdata=MultiDict([
            ('updated_at', 'blah')
        ]))
        assert form.validate(), form.errors

        # invalid datetime format
        form = FooForm(formdata=MultiDict([
            ('created_at', 'adsfasdfd')
        ]))
        assert not form.validate()
        assert 'created_at' in form.errors
        assert 'Not a valid datetime' in form.errors['created_at'][0]
        assert form.created_at._value() == 'adsfasdfd'

        # test objdata
        foo.created_at = None
        form = FooForm(obj=foo)
        assert form.created_at._value() == ''


def test_enum_field():

    class Animals(Enum):
        cat = 1
        dog = 2

    class FooForm(Form):
        animal = EnumField(Animals, allow_blank=True)

    # formdata
    form = FooForm(formdata=MultiDict([
        ('animal', '1'),
    ]))
    assert form.validate()
    # invalid choice
    form = FooForm(formdata=MultiDict([
        ('animal', '5'),
    ]))
    assert not form.validate()
    assert 'Invalid Choice' in form.errors['animal'][0]
    # allow_blank
    assert '__None' in {value for value, _, _ in form.animal.iter_choices()}

    # data
    form = FooForm(data=dict(animal=Animals.cat))
    assert form.animal.data == Animals.cat


def test_product_info_field():
    class FooForm(Form):
        info = ProductInfoField()

    def create_form(*data):
        return FooForm(formdata=MultiDict(data))

    # empty input
    form = create_form(
        ('info', ''),
    )
    assert form.validate(), form.errors
    assert form.info.data == ''

    # valid input
    form = create_form(
        ('info', 'a: b\nc: d'),
    )
    assert form.validate()
    assert form.info.data == 'a:b\nc:d'

    # invalid input
    for error_input in (
        'a',
        'a：b',  # chinese colon
    ):
        form = create_form(
            ('info', error_input)
        )
        assert not form.validate()
        assert '格式' in form.errors['info'][0]
        assert error_input in form.errors['info'][0]
