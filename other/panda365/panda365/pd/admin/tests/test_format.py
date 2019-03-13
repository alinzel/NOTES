from enum import Enum
from pd.admin.format import format_links, enum_formatter


def test_format_links():
    assert format_links() is None


def test_enum_formatter():
    class Foo1(Enum):
        a = 1
    assert enum_formatter('mock', Foo1.a) == \
        '<span class="label label-primary">a</span>'
    Foo1.a.admin_label = 'admin_a'
    assert 'admin_a' in enum_formatter('mock', Foo1.a)

    class Foo2(Enum):
        a = 1
    assert 'a' in enum_formatter('mock', Foo2.a)
    Foo2.a.label = 'label_a'
    assert 'label_a' in enum_formatter('mock', Foo2.a)
