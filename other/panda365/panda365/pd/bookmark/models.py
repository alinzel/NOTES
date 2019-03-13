from pd.sqla import db, CreateTimestampMixin


class Bookmark(CreateTimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'),
        nullable=False,
    )
    post = db.relationship(
        'Post', backref=db.backref(
            'bookmarks', cascade='all, delete-orphan', passive_deletes=True
        )
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False, index=True,
    )
    user = db.relationship(
        'User', backref=db.backref(
            'bookmarks', cascade='all, delete-orphan', passive_deletes=True
        )
    )

    UQ_NAME = 'uq_bookmark_user_id_post_id'

    __table_args__ = (
        db.UniqueConstraint('user_id', 'post_id', name=UQ_NAME),
    )
