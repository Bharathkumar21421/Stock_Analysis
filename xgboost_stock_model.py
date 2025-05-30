import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from prepare_data_for_xgb import data_dict

def train_xgb(X, y):
    model = XGBRegressor(objective='reg:squarederror', n_estimators=100)
    model.fit(X, y)
    return model

def plot_predictions(ticker, model, X, y, scaler):
    predicted = model.predict(X)
    predicted_prices = scaler.inverse_transform(predicted.reshape(-1, 1))
    real_prices = scaler.inverse_transform(y.reshape(-1, 1))

    plt.figure(figsize=(10, 5))
    plt.plot(real_prices, label='Real Price')
    plt.plot(predicted_prices, label='Predicted Price')
    plt.title(f"{ticker} Stock Price Prediction (XGBoost)")
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

def predict_future_days(model, last_sequence, days, scaler):
    future_preds = []
    current_seq = list(last_sequence)

    for _ in range(days):
        X_input = np.array(current_seq[-60:]).reshape(1, -1)
        pred = model.predict(X_input)[0]
        future_preds.append(pred)
        current_seq.append(pred)

    return scaler.inverse_transform(np.array(future_preds).reshape(-1, 1))
