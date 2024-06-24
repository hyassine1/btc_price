from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric, DateTime, Date, Boolean, Text, TIMESTAMP
from connection import engine
from datetime import datetime, timedelta
from sqlalchemy.sql import func



def create_tables():

    metadata = MetaData()

    klines = Table(
        "klines",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("symbol", String(10), nullable=False),
        Column("interval", String(10), nullable=False),
        Column("open_time", DateTime, nullable=False),
        Column("open_price", Numeric(18, 8), nullable=False),
        Column("high_price", Numeric(18, 8), nullable=False),
        Column("low_price", Numeric(18, 8), nullable=False),
        Column("close_price", Numeric(18, 8), nullable=False),
        Column("volume", Numeric(18, 8), nullable=False),
        Column("close_time", DateTime, nullable=False),
        Column("quote_asset_vol", Numeric(18, 8), nullable=False),
        Column("nb_trades", Numeric(18, 8), nullable=False),
        Column("created_at", TIMESTAMP, nullable=False, server_default=func.now())
        
    )


    predictions = Table(
        'predictions', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('forecast', Integer, nullable=False),
        Column('date', Date, nullable=False),
        Column("created_at", TIMESTAMP, nullable=False, server_default=func.now()),
    )

    symbols = Table(
        'symbols', metadata,
        Column('symbol', String, primary_key=True),
        Column('status', String),
        Column('baseAsset', String),
        Column('baseAssetPrecision', Integer),
        Column('quoteAsset', String),
        Column('quotePrecision', Integer),
        Column('quoteAssetPrecision', Integer),
        Column('baseCommissionPrecision', Integer),
        Column('quoteCommissionPrecision', Integer),
        Column('orderTypes', Text),   
        Column('icebergAllowed', Boolean),
        Column('ocoAllowed', Boolean),
        Column('otoAllowed', Boolean),
        Column('quoteOrderQtyMarketAllowed', Boolean),
        Column('allowTrailingStop', Boolean),
        Column('cancelReplaceAllowed', Boolean),
        Column('isSpotTradingAllowed', Boolean),
        Column('isMarginTradingAllowed', Boolean),
        Column('filters', Text),   
        Column('permissions', Text),   
        Column('permissionSets', Text),  # 
        Column('defaultSelfTradePreventionMode', Text),
        Column('allowedSelfTradePreventionModes', Text)   
    )

    klines_csv = Table(
        'klines_csv', metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('open_price', Numeric(18, 8), nullable=False),
        Column('high_price', Numeric(18, 8), nullable=False),
        Column('low_price', Numeric(18, 8), nullable=False),
        Column('close_price', Numeric(18, 8), nullable=False),
        Column('volume', Numeric(18, 8), nullable=False),
        Column('quote_asset_vol', Numeric(18, 8), nullable=False),
        Column('nb_trades', Integer, nullable=False),
        Column('taker_buy_base', Numeric(18, 8), nullable=False),
        Column('taker_buy_quote', Numeric(18, 8), nullable=False),
        Column('ignore', Integer, nullable=False),
        Column('open_time',  Numeric, nullable=False),
        Column('close_time',  Numeric, nullable=False)
    )

    users_table = Table(
        'users', metadata,
        Column('ID', Integer, primary_key=True, autoincrement=True, index=True),
        Column('username', String, unique=True, index=True),
        Column('hashed_password', String)
    )

    # Create the tables in the database
    metadata.create_all(engine)

    print("Tables have been created successfully")

