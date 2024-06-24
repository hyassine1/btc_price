import os
import csv
from connection import engine, Client
import datetime
from decimal import Decimal
from sqlalchemy import text

def save__CSV_Prices(folder_path):
    with engine.connect() as connection:

        # Iterate over each file in the folder
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                # Construct the full file path
                file_path = os.path.join(folder_path, filename)

                # Open the CSV file
                with open(file_path, 'r') as file:
                    # Create a CSV reader
                    csv_reader = csv.reader(file)

                    # Skip the header row if present
                    next(csv_reader)

                    # Iterate over each row in the CSV file
                    for row in csv_reader:
                        # Construct the SQL INSERT command
                        insert_query = text("""
                            INSERT INTO klines_csv (
                                open_time, open_price, high_price, low_price, close_price, volume, close_time, 
                                quote_asset_vol, nb_trades, taker_buy_base, taker_buy_quote, ignore
                            ) VALUES (
                                :open_time, :open_price, :high_price, :low_price, :close_price, :volume, :close_time, 
                                :quote_asset_vol, :nb_trades, :taker_buy_base, :taker_buy_quote, :ignore
                            )
                        """)
                        #print(row)
                        converted_row = {
                            'open_time': int(row[0]),  # open_time
                            'open_price': Decimal(row[1]),  # open_price
                            'high_price': Decimal(row[2]),  # high_price
                            'low_price': Decimal(row[3]),  # low_price
                            'close_price': Decimal(row[4]),  # close_price
                            'volume': Decimal(row[5]),  # volume
                            'close_time': int(row[6]),  # close_time
                            'quote_asset_vol': Decimal(row[7]),  # quote_asset_vol
                            'nb_trades': int(row[8]),  # nb_trades
                            'taker_buy_base': Decimal(row[9]),  # taker_buy_base
                            'taker_buy_quote': Decimal(row[10]),  # taker_buy_quote
                            'ignore': int(row[11])  # ignore
                        }
                        #print(converted_row)

                        # Execute the INSERT command with the current row's values
                        connection.execute(insert_query, converted_row)
                        #connection.close()

                    

'''
if __name__ == '__main__':

    folder_path = "C:/Users/HusseinYassine/Python Projects/binance/history_prices/spot/daily/klines/BTCUSDT/1m"
    print("Uploading Daily files...")
    save__CSV_Prices(folder_path)

    folder_path = "C:/Users/HusseinYassine/Python Projects/binance/history_prices/spot/Monthly/klines/BTCUSDT/1m"
    print("Uploading Monthly files...")
    save__CSV_Prices(folder_path)
'''