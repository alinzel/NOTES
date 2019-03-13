from pd.factory import BaseFactory
from .models import Bookmark


class BookmarkFactory(BaseFactory):

    class Meta:
        model = Bookmark
