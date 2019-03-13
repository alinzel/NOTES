from flask_admin.contrib.sqla.filters import FilterEqual


class EnumFilter(FilterEqual):

    def __init__(self, column, name, enum):
        self.enum = enum
        super().__init__(
            column, name,
            options=[(e.value, getattr(e, 'admin_label', e.name))
                     for e in enum])

    def clean(self, value):
        return self.enum(value)


class IntEnumFilter(EnumFilter):

    def clean(self, value):
        return super().clean(int(value))
