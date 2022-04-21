import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Object(SqlAlchemyBase):
    __tablename__ = 'objects'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    object = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    registry_number = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    longitude = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    latitude = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    region = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category_of_significance = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type_of_object = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_unesco = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    picture_src = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("users.id"))
    creator = orm.relation('User')
    comments = orm.relation("Comment", back_populates='object', cascade='all, delete')
