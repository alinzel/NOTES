from pd.api.schema import ModelSchema
from .models import Bookmark


class BookmarkSchema(ModelSchema):

    class Meta:
        model = Bookmark
        fields = (
            'id', 'post_id',
        )
