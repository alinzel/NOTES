from pd.api.schema import ModelSchema
from .models import Conf


class ConfSchema(ModelSchema):

    class Meta:
        model = Conf
        fields = (
            'name',
            'min_version',
            'latest_version',
            'description',
        )
