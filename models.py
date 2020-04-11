import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as SA_UUID

from app import db
from utils import now


class Column(db.Column):
    type_ = None
    primary_key: bool = False
    unique: bool = False
    nullable: bool = False

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault('type_', self.type_)
        kwargs.setdefault('primary_key', self.primary_key)
        kwargs.setdefault('unique', self.unique)
        kwargs.setdefault('nullable', self.nullable)
        super().__init__(*args, **kwargs)


class UUID(Column):
    type_ = SA_UUID()
    primary_key: bool = True
    unique: bool = True


class ForeignKey(Column):
    primary_key = False
    unique = False

    def __init__(self, reference: str, **kwargs) -> None:
        super().__init__(None, None, sa.ForeignKey(reference), **kwargs)


class DateCreated(Column):
    type_ = sa.DateTime()

    def __init__(self, **kwargs) -> None:
        kwargs['default'] = now
        super().__init__(**kwargs)


class Text(Column):
    type_ = sa.Text()


class Integer(Column):
    type_ = sa.BigInteger()


class Interval(Column):
    type_ = sa.Interval()
