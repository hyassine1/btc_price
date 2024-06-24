from binance_historical_data import BinanceDataDumper
import datetime

def dump_binance_data(start_date, end_date, tickers='BTCUSDT', path_dir="history_prices"):
    """
    Function to dump Binance data.
    """
    data_dumper = BinanceDataDumper(
        path_dir_where_to_dump=path_dir,
        asset_class="spot",  # spot, um, cm
        data_type="klines",  # aggTrades, klines, trades
        data_frequency="1m",
    )

    data_dumper.dump_data(
        tickers=tickers,
        date_start=start_date,
        date_end=end_date,
        is_to_update_existing=False,
        tickers_to_exclude=["UST"],
    )

'''
if __name__ == '__main__':

    start_date = datetime.date(year=2024, month=5, day=1)
    end_date = datetime.date(year=2024, month=6, day=23)

    dump_binance_data(start_date, end_date)
'''