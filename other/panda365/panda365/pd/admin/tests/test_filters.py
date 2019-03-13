from enum import Enum
from pd.admin.filters import EnumFilter, IntEnumFilter


def test_enum_filter():
    class Foo(Enum):
        a = 'x'
        b = 'y'

    f = EnumFilter('foo', 'foo', Foo)
    assert f.clean('x') == Foo.a


def test_int_enum_filter():
    class Foo(Enum):
        a = 1
        b = 2

    f = IntEnumFilter('foo', 'foo', Foo)
    assert f.clean(1) == Foo.a
