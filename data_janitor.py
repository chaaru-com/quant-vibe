import os
import sqlite3
import pandas as pd
import numpy as np

def clean_and_ingest():
    print("Ingesting raw data...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "nifty100_historical.csv")
    db_path = os.path.join(base_dir, "nifty100.db")
    
    # 1. Load CSV
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Raw CSV not found at {csv_path}")
        return

    # Check columns
    print("Columns in raw CSV:", df.columns)
    
    # 2. Parse Date
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    
    # Ensure ticker column exists since this is index data
    df['Ticker'] = 'NIFTY100'
    
    # 3. Apply BDD: clean missing prices
    price_cols = ['Open', 'High', 'Low', 'Close']
    for col in price_cols:
        if col in df.columns:
            # BDD Then: forward-fill followed by backward-fill fallback
            df[col] = df[col].ffill().bfill()
            
    # 4. Apply BDD: clean and smooth volume anomalies
    if 'Volume' in df.columns:
        # Replace negative values with 0
        df['Volume'] = df['Volume'].apply(lambda v: 0 if v < 0 or pd.isna(v) else v)
        
        # Smooth outliers (>5 std devs from rolling 20-day mean)
        rolling_mean = df['Volume'].rolling(20, min_periods=1).mean()
        rolling_std = df['Volume'].rolling(20, min_periods=1).std().fillna(0)
        rolling_median = df['Volume'].rolling(20, min_periods=1).median()
        
        # Identify anomalies
        is_anomaly = (df['Volume'] - rolling_mean).abs() > (5 * rolling_std)
        # BDD Then: Replace with rolling median
        df.loc[is_anomaly, 'Volume'] = rolling_median[is_anomaly]

    # 5. Ingest to local SQLite database
    conn = sqlite3.connect(db_path)
    # Write to table 'nifty100_ohlcv'
    df.to_sql('nifty100_ohlcv', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Pristine data successfully written to {db_path} in table 'nifty100_ohlcv'")
    print(f"Total rows ingested: {len(df)}")

if __name__ == "__main__":
    clean_and_ingest()
