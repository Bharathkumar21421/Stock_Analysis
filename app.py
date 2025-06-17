from flask import Flask, render_template, request
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import requests
import os

app = Flask(__name__)
NEWS_API_KEY = "0a0e85a371d647868ab1a8493229a000"

def get_live_data(ticker, n_lags=60):
    df = yf.download(ticker, period="2y")
    if df.empty or 'Close' not in df.columns:
        raise ValueError(f"Failed to retrieve valid data for {ticker}. Please try another stock or try again later.")
    df = df.reset_index()
    close_prices = df[['Close']].values

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(close_prices)

    X, y = [], []
    for i in range(n_lags, len(scaled)):
        X.append(scaled[i - n_lags:i, 0])
        y.append(scaled[i, 0])

    return np.array(X), np.array(y), scaler, df

def train_model(X, y):
    model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X, y)
    return model

def predict_future(model, last_sequence, days, scaler):
    future = []
    seq = list(last_sequence)
    for _ in range(days):
        input_seq = np.array(seq[-60:]).reshape(1, -1)
        pred = model.predict(input_seq)[0]
        future.append(pred)
        seq.append(pred)
    return scaler.inverse_transform(np.array(future).reshape(-1, 1))

def fetch_stock_news(ticker):
    query = f"{ticker} stock"
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    try:
        res = requests.get(url)
        data = res.json()
        news = []
        for article in data.get("articles", []):
            news.append({
                'title': article['title'],
                'link': article['url'],
                'description': article.get('description', '')
            })
        return news
    except Exception as e:
        print(f"⚠️ Error fetching news: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    ticker = request.form.get("stock", "META")
    today = datetime.today().strftime("%Y-%m-%d")
    news = []
    forecast = []

    try:
        X, y, scaler, df = get_live_data(ticker)
        model = train_model(X, y)
        last_seq = X[-1]
        forecast = predict_future(model, last_seq, 7, scaler)
        future_dates = pd.date_range(df['Date'].iloc[-1] + pd.Timedelta(days=1), periods=7)
        forecast = list(zip(future_dates.strftime("%Y-%m-%d"), forecast.flatten()))

        plt.style.use('seaborn-v0_8-muted')
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(future_dates, [p[1] for p in forecast], marker='o', color='#2E7D32', linewidth=2.5, label="Forecast")
        ax.set_title(f"{ticker} 7-Day Stock Forecast", fontsize=14, fontweight='bold')
        ax.set_xlabel("Date")
        ax.set_ylabel("Predicted Price")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='upper left')
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.savefig("static/forecast.png", bbox_inches='tight', dpi=120)
        plt.close()

        news = fetch_stock_news(ticker)

    except ValueError as e:
        return render_template("index.html",
                               stock=ticker,
                               forecast=[],
                               today=today,
                               news=[],
                               error=str(e))

    return render_template("index.html",
                           stock=ticker,
                           forecast=forecast,
                           today=today,
                           news=news,
                           error=None)

if __name__ == "__main__":
    app.run(debug=True)
