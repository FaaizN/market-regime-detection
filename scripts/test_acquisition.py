import sys
import os
import pandas as pd
from datetime import datetime, timedelta


# Add src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.acquisition import MarketDataFetcher

def main():
    print("Testing Market Data Fetcher...")

    # Create a fetcher instance
    fetcher = MarketDataFetcher({})

    # Define a date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days = 365)).strftime('%Y-%m-%d')

    # Fetch the sample data
    print(f"Fetching data from {start_date} to {end_date}")

    # Test individual stock data
    print("\nFetching individual stock data for AAPL...")
    apple_data = fetcher.fetch_market_data('AAPL', start_date, end_date)
    print(f"Shape: {apple_data.shape}")
    print(apple_data.head())

    # Test market indices data
    print("\nFetching market indices...")
    indices = fetcher.fetch_market_indices(['SPY', '^VIX'], start_date, end_date)
    print(f"Shape: {indices.shape}")
    print(indices.head())

    # Test combined dataset
    print("\nFetching combined dataset...")
    combined = fetcher.fetch_combined_dataset(['AAPL', 'MSFT', 'GOOGL'], 
                                              ['SPY', '^VIX'], 
                                              start_date)
    print(f"Shape: {combined.shape}")
    print(combined.head())

    # Save the sample data to the CSV
    print("\nSaving sample data to data/raw/sample_data.csv")
    os.makedirs('data/raw', exist_ok = True)
    combined.to_csv('data/raw/sample_data.csv')

    print("\nTest completed sucessfully!")

if __name__ == "__main__":
    main()