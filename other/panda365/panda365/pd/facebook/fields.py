from marshmallow import fields
from pd.facebook.models import Base


class Gid(fields.String):
    default_error_messages = {
        'invalid': 'invalid gid'
    }

    def _deserialize(self, value, attr, obj):
        value = super()._deserialize(value, attr, obj)
        ret = Base.decode_gid(value)
        if not ret:
            self.fail('invalid')
        return ret
