import pandas as pd
import numpy as np
import mysql.connector
from sklearn.preprocessing import MinMaxScaler
from config import MYSQL_CONFIG

def load_stock_data(ticker):
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    query = f"SELECT * FROM {ticker.lower()}_stock_data ORDER BY Date"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def create_lag_features(df, n_lags=60):
    data = df[['Close']].values
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(n_lags, len(scaled_data)):
        X.append(scaled_data[i - n_lags:i, 0])
        y.append(scaled_data[i, 0])

    return np.array(X), np.array(y), scaler

# Dictionary of prepared data
data_dict = {}

for ticker in ['META', 'AAPL', 'AMZN']:
    print(f"\n📊 Preparing data for {ticker}...")
    df = load_stock_data(ticker)
    X, y, scaler = create_lag_features(df)
    data_dict[ticker] = {
        'df': df,
        'X': X,
        'y': y,
        'scaler': scaler
    }
    print(f"✅ {ticker}: {X.shape[0]} sequences prepared.")
