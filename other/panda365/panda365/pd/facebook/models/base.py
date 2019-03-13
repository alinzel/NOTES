import base64
import re
from sqlalchemy.ext.hybrid import hybrid_property
from pd.sqla import db, CreateTimestampMixin, ignore_integrity_error


_uq_fb_id_pattern = re.compile('uq_(\w+)_fb_id')


class Base(CreateTimestampMixin, db.Model):
    __abstract__ = True
    fb_id = db.Column(db.Text, unique=True)

    @classmethod
    def upsert(cls, fb_id, **data):
        obj = cls.query.filter_by(fb_id=fb_id).first()
        if not obj:
            obj = cls()
            db.session.add(obj)
        obj.fb_id = fb_id
        for k, v in data.items():
            setattr(obj, k, v)
        return obj

    @classmethod
    def try_insert(cls, **kwargs):
        """
        Try to insert the current object. If object already exists(violates
        unique on fb_id), the transaction is rollback.
        """
        obj = cls(**kwargs)
        with ignore_integrity_error(_uq_fb_id_pattern):
            db.session.add(obj)
            db.session.flush()
            return obj

    @classmethod
    def fb_query(cls, fb_id):
        return cls.query.filter(cls.fb_id == fb_id)

    @classmethod
    def encode_gid(cls, mapper_name, id):
        return base64.b64encode(
            '{}|{}'.format(mapper_name, id).encode()
        ).decode()

    @classmethod
    def decode_gid(cls, gid):
        """
        returns: tuple (mapper_class, pk)
        """
        try:
            decoded = base64.b64decode(gid).decode()
            mapper_name, ident = decoded.split('|')
            return cls._decl_class_registry[mapper_name], int(ident)
        except (KeyError, ValueError, UnicodeDecodeError):
            pass

    @property
    def gid(self):
        return self.encode_gid(self.__class__.__name__, self.id)

    @hybrid_property
    def is_from_fb(self):
        return self.fb_id != None  # noqa

    def __repr__(self):
        return '{}[{}]'.format(self.__tablename__, self.id)


class ActionParentMixin:

    def add_action(self, action_cls, **kwargs):
        action = action_cls(parent_id=self.id,
                            parent_type=self.__class__.__name__, **kwargs)
        num_col = getattr(
            self.__table__.c, '{}s_num'.format(action_cls.__name__.lower()))
        with ignore_integrity_error(_uq_fb_id_pattern):
            db.session.add(action)
            self.query.filter_by(id=self.id).update({
                num_col: num_col + 1,
            })
            db.session.flush()
            return action

    def remove_action(self, action_cls, **kwargs):
        action = action_cls.query.filter_by(parent=self, **kwargs).first()
        num_col = getattr(
            self.__table__.c, '{}s_num'.format(action_cls.__name__.lower()))
        if action:
            self.query.filter_by(id=self.id).update({
                num_col: num_col - 1,
            })
            db.session.delete(action)
            db.session.flush()
            return True
        return False
