from connection import engine
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


sql_query = "SELECT * FROM klines "

df = pd.read_sql(sql_query, engine)

engine.dispose()


#Data checking and cleaning
print(df.shape)
df.info()
print(df.describe())
print(df.isnull().sum())
df.dropna(inplace=True)

#apply the prediction system
required = ['open_price', 'high_price', 'low_price', 'volume', 'nb_trades']
output = 'close_price'

x_train, x_test, y_train, y_test = train_test_split(df[required],df[output],test_size = 0.3)

model = LinearRegression()
model.fit(x_train, y_train)
model.score(x_test, y_test)

plt.plot(df["close_time"][-400:-60], df["close_price"][-400:-60], color='goldenrod', lw=2)
#plt.plot(future["Timestamp"], prediction, color='deeppink', lw=2)
plt.title("Bitcoin Price over time", size=10)
plt.xlabel("Time", size=10)
plt.ylabel("$ Price", size=10)

