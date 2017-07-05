# coding=utf-8

"""
字段, id, uuid, category, site, title(可为空), description(可为空), create_time, download
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, func, BOOLEAN
from sqlalchemy.orm import relationship, backref
import datetime
from sqlalchemy_utils import ChoiceType
import datetime

Base = declarative_base()


class ViedoModel(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False)
    category = Column(String)
    site = Column(String)
    title = Column(String)
    desc = Column(String)
    create_on = Column(DateTime, default=datetime.datetime.now)
    url = Column(String)
    download = Column(BOOLEAN, default=False)
    path = Column(String)

    def __repr__(self):
        return '<Video %s>' % self.title.encode('utf-8')
