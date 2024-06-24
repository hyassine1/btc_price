from connection import engine
from datetime import datetime, timedelta

def save__CSV_Prices():

    result = engine.execute("SELECT * FROM klines_csv ")
    column_names = result.keys()
    #print(column_names)

    symbol = 'BTCUSDT'
    interval = '1m'

    for row in result:
        open_time =datetime.fromtimestamp(row[11]/1000) 
        close_time=datetime.fromtimestamp(row[12]/1000)

        #print(row[0])
        sql = f"""INSERT INTO klines (symbol, interval, open_time, open_price, high_price, low_price, close_price, volume, close_time, quote_asset_vol, nb_trades ) 
        VALUES ('{symbol}','{interval}','{open_time}', '{row[1]}', '{row[2]}', '{row[3]}', '{row[4]}', '{row[5]}', '{close_time}', '{row[6]}', '{row[7]}')
        """
        engine.execute(sql)
    result.close()
    engine.dispose()

'''
if __name__ == '__main__':
    save__CSV_Prices()
'''