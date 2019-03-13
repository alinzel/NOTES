from pd.sqla import db, translation_hybrid, CreateTimestampMixin
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy_utils as su


class ProductMedia(db.Model):
    url = db.Column(db.Text, nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'),
        nullable=False,
    )
    product = db.relationship(
        'Product',
        backref=db.backref(
            'media', cascade='all, delete-orphan', passive_deletes=True,
            order_by='ProductMedia.id',
        )
    )


class Product(CreateTimestampMixin, db.Model):
    title_translations = db.Column(JSONB)
    title = translation_hybrid(title_translations)
    info_translations = db.Column(JSONB)
    info = translation_hybrid(info_translations)
    description_translations = db.Column(JSONB)
    description = translation_hybrid(info_translations)

    comments = db.relationship(
        'Comment',
        primaryjoin=(
            "and_(Comment.parent_id == foreign(Product.id), Comment.parent_type == 'Product')"  # noqa
        ),
        uselist=True,
        single_parent=True,
        cascade='all, delete-orphan',
    )

    @su.aggregated('comments', db.Column(db.Integer, doc='评论数', default=0))
    def comments_num(self):
        return db.func.count('1')

    @property
    def media_urls(self):
        return [m.url for m in self.media]

    def __repr__(self):
        return '[{}]{}'.format(self.id, self.title[:20])


class SpecOption(db.Model):
    value_translations = db.Column(JSONB)
    value = translation_hybrid(value_translations)

    def __repr__(self):
        return '{}'.format(self.value)


class Spec(db.Model):
    name_translations = db.Column(JSONB)
    name = translation_hybrid(name_translations)

    def __repr__(self):
        return '{}'.format(self.name)


class Category(db.Model):
    name_translations = db.Column(JSONB)
    name = translation_hybrid(name_translations)
    sort_weight = db.Column(db.Float, default=0, server_default='0',
                            nullable=False, doc='排序权重默认是0')

    def __repr__(self):
        return '[{}]{}'.format(self.id, self.name)
