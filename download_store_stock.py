import yfinance as yf
import mysql.connector
from config import MYSQL_CONFIG

def fetch_and_store_stock(ticker):
    print(f"📥 Downloading data for {ticker}...")
    df = yf.download(ticker, start="2020-01-01", end="2024-12-31")
    df.reset_index(inplace=True)

    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    table_name = ticker.lower() + "_stock_data"
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f'''
        CREATE TABLE {table_name} (
            Date DATE,
            Open FLOAT,
            High FLOAT,
            Low FLOAT,
            Close FLOAT,
            Volume BIGINT
        )
    ''')

    for _, row in df.iterrows():
        cursor.execute(f'''
            INSERT INTO {table_name} (Date, Open, High, Low, Close, Volume)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            row.iloc[0].to_pydatetime().date(),  # Date
            float(row.iloc[1]),  # Open
            float(row.iloc[2]),  # High
            float(row.iloc[3]),  # Low
            float(row.iloc[4]),  # Close
            int(row.iloc[5])     # Volume
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Inserted {len(df)} rows into `{table_name}`.\n")

# Fetch and store data for META, AAPL, AMZN
for ticker in ['META', 'AAPL', 'AMZN']:
    fetch_and_store_stock(ticker)
