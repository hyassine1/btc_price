from fastapi import Depends, FastAPI, HTTPException, status, Form, Header, Request,Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, date
from fastapi.responses import JSONResponse
import pandas as pd 
from typing import List, Optional
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, func
from jose import JWTError, jwt
from pprint import pprint 
import  models
from schemas import Token, TokenData, User, UserCreate, UserInDB, MyException, PriceResponse
from utils import get_password_hash, authenticate_user, create_access_token
from connection import engine, Client, get_db
import json
from statsmodels.tsa.arima.model import ARIMA
import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import os


api = FastAPI(title="Datascientest Binance API", description="Predicition BTC Price",    version="1.0.1",openapi_tags=[
    {
        'name': 'Access Details',
        'description': 'Get Access to the system'
    },
    {
        'name': 'Prediction Model',
        'description': 'functions for the Model'
    }
]) 

SECRET_KEY = "Binan@ce#2o24"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Get_token")



@api.exception_handler(MyException)
def MyExceptionHandler(
    request: Request,
    exception: MyException
    ):
    return JSONResponse(
        status_code=418,
        content={
            'url': str(request.url),
            'name': exception.name,
            'message': 'This error is my own', 
            'date': exception.date
        }
    )

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def insert_kline_data(kline_data, symbol, interval):
    if interval == 'Client.KLINE_INTERVAL_1MINUTE':
        interval = '1m'

    rows_to_insert = []

    for kline in kline_data:
        try:
            open_time = datetime.fromtimestamp(kline[0] / 1000)
            close_time = datetime.fromtimestamp(kline[6] / 1000)
        except OSError as e:
            print(f"Error converting timestamp: {e}")
            continue

        row = {
            'symbol': symbol,
            'interval': interval,
            'open_time': open_time,
            'open_price': kline[1],
            'high_price': kline[2],
            'low_price': kline[3],
            'close_price': kline[4],
            'volume': kline[5],
            'close_time': close_time,
            'quote_asset_vol': kline[7],
            'nb_trades': kline[8],
        }
        rows_to_insert.append(row)

    # Use SQLAlchemy's bulk_insert_mappings for efficient bulk insert
    with engine.connect() as connection:
        with Session(connection) as session:
            session.bulk_insert_mappings(models.Kline, rows_to_insert)
            session.commit()

def truncate_table(table_name:str):

    with engine.connect() as connection:
        sql = text(f"DELETE FROM {table_name}")
        connection.execute(sql)
    return {"Table truncated:": table_name}

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

    #print(df_combined)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'plot_{timestamp}.png'
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
    plt.savefig(filename) 

    return filename



@api.post("/Get_token", name="Login to get Token", response_model=Token,tags=['Access Details'])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(SECRET_KEY, ALGORITHM,  data={"sub": user.username}, expires_delta=access_token_expires    )
    return {"access_token": access_token, "token_type": "bearer"}

@api.post("/Create_new_user/", name="Create New user", tags=['Access Details'])
async def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create user model
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    
    # Add user to the database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"Username Created": user.username}

@api.get("/get_list_users/", name="Get Users List", tags=['Access Details'])
async def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(models.User).all()

@api.delete("/delete_users/", name="Delete Users", tags=['Access Details'])
def delete_user(user_ids: List[int], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted_users = []
    for user_id in user_ids:
        user = db.query(models.User).filter(models.User.ID == user_id).first()
        if user:
            db.delete(user)
            deleted_users.append(user_id)
    db.commit()
    return {"message": "Users deleted successfully", "deleted_users": deleted_users}



@api.post("/Save_prices_binance/", name="Get prices from binance", tags=['Prediction Model'])
def save_price_binance(start_time:date, end_time:date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    symbol   = "BTCUSDT"  
    interval = Client.KLINE_INTERVAL_1MINUTE  
    limit    = 1000

    start_time       = datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)
    end_time         = datetime(end_time.year, end_time.month, end_time.day, 23, 59, 59)

    Klines_data = []
    while start_time <= end_time:
        start_timestamp  = int(start_time.timestamp() * 1000)
        end_timestamp    = int(end_time.timestamp() * 1000)

        klines = Client.get_klines(symbol=symbol, interval=interval, limit=limit, startTime=start_timestamp,endTime=end_timestamp)
        insert_kline_data(klines, symbol,interval )

        kline_headers = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 
                    'Quote Asset Volume','Number of Trades', 'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore']
        df=pd.DataFrame(klines,columns=kline_headers)
        
        Klines_data.extend(klines)
        start_time= datetime.fromtimestamp(Klines_data[-1][6] / 1000)
    return {"Prices saved"}

@api.post("/Save_symbols_binance/", name="Get symbols from binance", tags=['Prediction Model'])
def save_symbols_binance( db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Get Symbols Specs
    exchange_info = Client.get_exchange_info()
    df=pd.DataFrame(exchange_info['symbols'])

    table_name = 'symbols'

    df['orderTypes'] = df['orderTypes'].apply(json.dumps)
    df['filters'] = df['filters'].apply(json.dumps)
    df['permissions'] = df['permissions'].apply(json.dumps)
    df['defaultSelfTradePreventionMode'] = df['defaultSelfTradePreventionMode'].apply(json.dumps)
    df['allowedSelfTradePreventionModes'] = df['allowedSelfTradePreventionModes'].apply(json.dumps)

    truncate_table("symbols")
    df.to_sql(table_name, engine, if_exists='append', index=False)

    return {"Symbols Saved"}

@api.get("/Get_daily_prices/", name="Get prices from DB", tags=['Prediction Model'])
def get_prices(open_time:date, end_time:date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    subquery = (
        db.query(
            func.date(models.Kline.close_time).label('date'),
            func.max(models.Kline.close_time).label('max_close_time')
        )
        .filter(func.date(models.Kline.close_time).between(open_time, end_time))
        .group_by(func.date(models.Kline.close_time))
        .subquery()
    )

    last_prices = (
        db.query(
            subquery.c.date,
            models.Kline.close_price,
            models.Kline.close_time
        )
        .join(models.Kline, and_(
            subquery.c.date == func.date(models.Kline.close_time),
            subquery.c.max_close_time == models.Kline.close_time
        ))
        .all()
    )

    if not last_prices:
        raise HTTPException(status_code=404, detail="No prices found for the given time range")
    response_data = [
        {
            "date": price.date,
            "close_price": price.close_price,
            "close_time": price.close_time
        }
        for price in last_prices
    ]

    return [PriceResponse(**data) for data in response_data]

@api.get("/Get_predcited_prices/", name="Get predcited prices from DB", tags=['Prediction Model'])
def get_predictions(open_time:date, end_time:date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(models.Prediction).filter(models.Prediction.date.between(open_time, end_time)).all()


@api.post("/run_model/", name="Run Arima Model", tags=['Prediction Model'])
def get_predictions( db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    generate_forecast_plot()

    return {"succssefully loaded and predicted prices saved to DB"}


@api.get("/Plot_predicted_price/", name="Get last 7 Predicted Price", tags=['Prediction Model'])
def plot_predictions( db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_name = plot_actual_and_predicted_prices()

    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, file_name)
    return {"plot image Saved", file_path}