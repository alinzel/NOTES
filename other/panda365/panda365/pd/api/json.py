from arrow import Arrow
from flask.json import JSONEncoder as _BaseEncoder


class JSONEncoder(_BaseEncoder):

    def default(self, obj):
        if isinstance(obj, Arrow):
            return obj.isoformat()
        return super().default(obj)  # pragma: no cover
