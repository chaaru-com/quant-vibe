import os
import yfinance as yf
import pandas as pd

def fetch_nifty_data():
    print("Fetching Nifty 100 historical data...")
    ticker = "^CNX100"
    
    # Download data for max timeframe
    data = yf.download(ticker, period="max", interval="1d")
    
    # Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    # Drop completely empty rows
    data.dropna(subset=['Close'], inplace=True)
    
    # Save the data to a CSV file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(base_dir, "nifty100_historical.csv")
    data.to_csv(output_filename)
    
    print(f"Success! Data saved to {output_filename}")
    print(f"Total trading days retrieved: {len(data)}")

if __name__ == "__main__":
    fetch_nifty_data()


