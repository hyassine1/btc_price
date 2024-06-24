import pandas as pd
from datetime import datetime, timedelta
from connection import engine, Client


def insert_kline_data(kline_data,symbol, interval ):

    symbol=symbol
    if interval=='Client.KLINE_INTERVAL_1MINUTE':
        interval='1m'

    with engine.connect() as connection:
        for kline in kline_data:
            try:
                open_time = datetime.fromtimestamp(kline[0]/1000)
            except OSError as e:
                print(f"Error converting timestamp: {e}")
                continue

            open_price = kline[1]
            high_price = kline[2]
            low_price = kline[3]
            close_price = kline[4]
            volume = kline[5]
            try:
                close_time = datetime.fromtimestamp(kline[6]/1000)
            except OSError as e:
                print(f"Error converting timestamp: {e}")
                continue
            quote_asset_vol = kline[7]
            nb_trades = kline[8]

            # Create the SQL query for insertion
            sql = f"INSERT INTO klines (symbol, interval, open_time, open_price, high_price, low_price, close_price, volume, close_time, quote_asset_vol, nb_trades ) VALUES ('{symbol}','{interval}','{open_time}', '{open_price}', '{high_price}', '{low_price}', '{close_price}', '{volume}', '{close_time}', '{quote_asset_vol}', '{nb_trades}')"

            # Execute the SQL query
            connection.execute(sql)



symbol   = "BTCUSDT"  
#symbol1  = "ETHUSDT" 
interval = Client.KLINE_INTERVAL_1MINUTE  
limit    = 1000

today            = datetime.now()
yesterday        = today - timedelta(days=1)

start_time       = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
end_time         = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

Klines_data = []
while start_time <= end_time:
    start_timestamp  = int(start_time.timestamp() * 1000)
    end_timestamp    = int(end_time.timestamp() * 1000)

    klines = Client.get_klines(symbol=symbol, interval=interval, limit=limit, startTime=start_timestamp,endTime=end_timestamp)
    insert_kline_data(klines, symbol,interval )
    print(klines)
    kline_headers = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 
                 'Quote Asset Volume','Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore']
    df=pd.DataFrame(klines,columns=kline_headers)
 

    Klines_data.extend(klines)
    start_time= datetime.fromtimestamp(Klines_data[-1][6] / 1000)

"""
kline_headers = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 
                 'Quote Asset Volume','Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore']
df=pd.DataFrame(klines,columns=kline_headers)
print(df.head())
"""




