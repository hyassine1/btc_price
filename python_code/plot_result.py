import pandas as pd
from datetime import datetime, timedelta
from connection import engine, Client
import matplotlib.pyplot as plt
import io
import base64


def plot_actual_and_predicted_prices():

    query = f'''
    SELECT
        date(close_time) AS date,
        close_price,
        close_time
    FROM
        klines
    WHERE
        (date(close_time), close_time) IN (
            SELECT
                date(close_time) AS date,
                MAX(close_time) AS max_close_time
            FROM
                klines
            
            GROUP BY
                date(close_time)
        )
    ORDER BY
        date desc limit 10;
    '''

    query_predictions = 'SELECT date, forecast FROM predictions ORDER BY date desc LIMIT 7'

    df_klines = pd.read_sql_query(query, engine)
    df_predictions = pd.read_sql_query(query_predictions, engine)

    df_klines['type'] = 'actual'
    df_predictions['type'] = 'predicted'

    df_predictions.columns = ['date', 'close_price', 'type']

    df_combined = pd.concat([df_predictions,df_klines]).reset_index(drop=True)

    print(df_combined)

    # Plot the prices
    plt.figure(figsize=(10, 5))
    for label, df in df_combined.groupby('type'):
        plt.plot(df['date'], df['close_price'], marker='o', label=label)
    plt.title('Actual and Predicted Prices from klines and predictions')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig('plot.png')

start_date = '2024-05-20'
end_date = '2024-06-01'

plot_actual_and_predicted_prices( )