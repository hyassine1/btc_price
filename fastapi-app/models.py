from sqlalchemy import Column, Integer, String, DateTime, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    ID = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Kline(Base):
    __tablename__ = 'klines'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    interval = Column(String)
    open_time = Column(DateTime, index=True)
    open_price = Column(Numeric(18, 8))
    high_price = Column(Numeric(18, 8))
    low_price = Column(Numeric(18, 8))
    close_price = Column(Numeric(18, 8))
    volume = Column(Numeric(18, 8))
    close_time = Column(DateTime)
    quote_asset_vol = Column(Numeric(18, 8))
    nb_trades = Column(Numeric(18, 8))


class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, index=True)
    forecast = Column(Numeric)
    date = Column(Date)