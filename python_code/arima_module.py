import pandas as pd
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import matplotlib
import matplotlib.pyplot as plt
from connection import engine
from sqlalchemy import text

def load_data():
    query = "SELECT * FROM klines WHERE symbol = 'BTCUSDT' ORDER BY close_time ASC"
    df = pd.read_sql(query, con=engine)
    
    df['timestamp'] = pd.to_datetime(df['close_time'])
    df.set_index('timestamp', inplace=True)
    
    df['close_price'] = pd.to_numeric(df['close_price'], errors='coerce')
    df.dropna(subset=['close_price'], inplace=True)
    
    return df

def generate_forecast_plot():
    df = load_data()
    
    df_daily = df.resample('D').agg({
        'symbol': 'first',
        'open_price': 'mean',
        'high_price': 'mean',
        'low_price': 'mean',
        'close_price': 'mean',
        'volume': 'sum'
    })

    df_daily['close_price'] = pd.to_numeric(df_daily['close_price'], errors='coerce')
    df_daily.dropna(subset=['close_price'], inplace=True)

    train_size = int(len(df_daily['close_price']) * 1)
    data = df_daily['close_price'][0:train_size]

    model = ARIMA(data, order=(5,1,0))
    fit_model = model.fit()

    forecast = fit_model.forecast(steps=7)
    
    future_dates = pd.date_range(start=data.index[-1] + timedelta(days=1), periods=7, freq='D')
    forecast_df = pd.DataFrame({'date': future_dates, 'forecast': forecast})
    
    insert_sql = """
    INSERT INTO predictions (date, forecast)
    VALUES (:date, :forecast)
    """

    with engine.connect() as connection:
        with connection.begin() as transaction:
            try:
                for row in forecast_df.itertuples(index=False):
                    connection.execute(text(insert_sql), {'date': row.date, 'forecast': row.forecast})
                transaction.commit()
                print("Forecast values inserted successfully.")
            except Exception as e:
                transaction.rollback()
                print(f"Error occurred: {e}")

    future_dates = pd.date_range(start=data.index[-1], periods=7, freq='D')
    extended_index = data.index.union(future_dates)

    matplotlib.use('TkAgg')
    plt.plot(data.index, data, label='Historical Data')
    plt.plot(extended_index[-7:], forecast, label='Forecast', linestyle='--')

    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title('ARIMA Forecast with Next 7 Days Prediction')
    plt.legend()
    plt.grid(True)
    
    plot_path = "forecast_plot.png"
    plt.savefig(plot_path)
    plt.close()

    return plot_path

if __name__ == '__main__':
    generate_forecast_plot()