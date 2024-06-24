import json
import pandas as pd
from connection import engine, Client
from pprint import pprint 

def truncate_table(table_name:str):

    with engine.connect() as connection:
        sql = f"delete from {table_name}"
        connection.execute(sql)
    return {"Table truncated:": table_name}


# Get Symbols Specs
exchange_info = Client.get_exchange_info()
df=pd.DataFrame(exchange_info['symbols'])
pprint(df.head())

dtypes = df.dtypes
print(dtypes)

table_name = 'symbols'


df['orderTypes'] = df['orderTypes'].apply(json.dumps)
df['filters'] = df['filters'].apply(json.dumps)
df['permissions'] = df['permissions'].apply(json.dumps)
df['defaultSelfTradePreventionMode'] = df['defaultSelfTradePreventionMode'].apply(json.dumps)
df['allowedSelfTradePreventionModes'] = df['allowedSelfTradePreventionModes'].apply(json.dumps)

truncate_table("symbols")

df.to_sql(table_name, engine, if_exists='append', index=False)