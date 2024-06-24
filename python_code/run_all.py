import metadata
import historical_get_csv
import historical_import_db
import historical_data_cleaning
import datetime
from connection import engine, Client
from sqlalchemy import text, and_, func
import os
current_directory = os.getcwd()
data_folder_path = os.path.join(current_directory, 'history_prices')

def insert_user(username, hashed_password):
    with engine.connect() as connection:
        sql = text(f"INSERT INTO users (username, hashed_password ) VALUES ('{username}','{hashed_password}')")
        connection.execute(sql)


if __name__ == "__main__":

    metadata.create_tables()

    #create admin user that will use it for FastAPI
    insert_user("admin","$2b$12$xYwfIxvlam3oMNpszoSwr.n0pwtQEcfWuEUa8H/7bo1dgphE/BeFq") #password=admin2

    #Get Historical Data 
    start_date = datetime.date(year=2024, month=4, day=1)
    end_date = datetime.date(year=2024, month=6, day=22)
    historical_get_csv.dump_binance_data(start_date, end_date)

    #Upload Data to Temp Table
    folder_path = data_folder_path+"/spot/daily/klines/BTCUSDT/1m"
    folder_path2 = data_folder_path+"/spot/Monthly/klines/BTCUSDT/1m"

    print("Uploading Daily files...")
    historical_import_db.save__CSV_Prices(folder_path)

    print("Uploading Monthly files...")
    historical_import_db.save__CSV_Prices(folder_path2)


    #Save Data to Main Table: Kline
    historical_data_cleaning.save__CSV_Prices()
    print("Historical Data saved into Klines Table")