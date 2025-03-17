import os
import sys
import argparse
import pandas as pd

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.feature_engineering import FeatureEngineer

def main():
    parser = argparse.ArgumentParser(description='Process market data and engineer features')
    parser.add_argument('--input_path', type=str, default='data/raw/market_data.csv',
                       help='Path to the input raw market data CSV file')
    parser.add_argument('--output_dir', type=str, default='data/features',
                       help='Directory to save the processed features')
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load the raw data
    print(f"Loading data from {args.input_path}")
    data = pd.read_csv(args.input_path, index_col=0, parse_dates=True)
    
    # Initialize the feature engineer
    engineer = FeatureEngineer()
    
    # Process the data
    print("Processing data and engineering features...")
    processed_data = engineer.process_data(data)
    
    # Save the processed data
    output_path = os.path.join(args.output_dir, 'market_features.csv')
    processed_data.to_csv(output_path)
    print(f"Features saved to {output_path}")
    
    return processed_data

if __name__ == "__main__":
    main()