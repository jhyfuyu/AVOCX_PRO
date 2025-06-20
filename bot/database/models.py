from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy import Column, Integer, String, Boolean
from typing import List, Any

DB_NAME = "sqlite:///main.db"
engine = create_engine(DB_NAME)


class Base(DeclarativeBase):
    pass


class Channels(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    admin = Column(String, unique=False, index=True)
    income_from_ad = Column(Integer, unique=False, index=True, default=0)
    buys_exp = Column(Integer, unique=False, index=True, default=0)
    ad_sells = Column(Integer, unique=False, index=True, default=0)
    ad_buys = Column(Integer, unique=False, index=True, default=0)


class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    telegram_id = Column(String, unique=True, index=True)
    income_from_ad = Column(Integer, unique=False, index=True, default=0)
    buys_exp = Column(Integer, unique=False, index=True, default=0)
    ad_sells = Column(Integer, unique=False, index=True, default=0)
    ad_buys = Column(Integer, unique=False, index=True, default=0)
    channel_for_creative = Column(String, unique=False, index=True)
    auto_reception = Column(Boolean, unique=False, index=True)


class Creatives(Base):
    __tablename__ = 'creatives'
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=False, index=True)
    text = Column(String, unique=False, index=True)
    url = Column(String, unique=False, index=True)
    media = Column(String, unique=False, index=True)


class Buys(Base):
    __tablename__ = 'buys'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=False, index=True)
    channel = Column(String, unique=False, index=True)
    datetime = Column(String, unique=False, index=True)
    price = Column(String, unique=False, index=True)
    creative = Column(Integer, unique=False, index=True)
    admin = Column(String, unique=False, index=True)
    link = Column(String, unique=False, index=True)
    theme = Column(String, unique=False, index=True)
    started = Column(Boolean, unique=False, index=True)


base = Base()
Base.metadata.create_all(engine)
