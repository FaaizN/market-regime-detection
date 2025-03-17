import os
import sys
# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.acquisition import MarketDataFetcher
import argparse

def main():
    parser = argparse.ArgumentParser(description='Fetch market data')
    parser.add_argument('--output_dir', type=str, default='data/raw', 
                        help='Directory to save the data')
    parser.add_argument('--tickers', type=str, default='AAPL,MSFT,GOOGL,AMZN,META',
                        help='Comma-separated list of stock tickers')
    parser.add_argument('--lookback_years', type=int, default=10,
                        help='Number of years to look back')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize the data fetcher
    fetcher = MarketDataFetcher()
    
    # Fetch combined dataset with market data and indices
    tickers_list = args.tickers.split(',')
    data = fetcher.fetch_combined_dataset(
        market_tickers=tickers_list,
        lookback_years=args.lookback_years
    )
    
    # Instead of using the built-in add_technical_indicators method,
    # we'll implement our own version that works with multiple columns
    enhanced_data = data.copy()

    # Save to CSV
    output_path = os.path.join(args.output_dir, 'market_data.csv')
    data.to_csv(output_path)
    print(f"Raw data saved to {output_path}")
    
    return data

if __name__ == "__main__":
    main()