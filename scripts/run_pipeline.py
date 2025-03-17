import os 
import argparse
import subprocess

def main():

    parser = argparse.ArgumentParser(description='Run the full data pipeline')
    parser.add_argument('--tickers', type=str, default='AAPL,MSFT,GOOGL,AMZN,META,NVDA,TSLA',
                       help='Comma-separated list of stock tickers')
    parser.add_argument('--lookback_years', type=int, default=10,
                       help='Number of years to look back')
    parser.add_argument('--raw_dir', type=str, default='data/raw',
                       help='Directory to save raw data')
    parser.add_argument('--features_dir', type=str, default='data/features',
                       help='Directory to save processed features')
    args = parser.parse_args()
    
    # Create directories if they don't exist
    os.makedirs(args.raw_dir, exist_ok=True)
    os.makedirs(args.features_dir, exist_ok=True)
    
    # Step 1: Run data acquisition
    print("Step 1: Running data acquisition...")
    acquisition_cmd = [
        "python", "scripts/run_acquisition.py",
        "--output_dir", args.raw_dir,
        "--tickers", args.tickers,
        "--lookback_years", str(args.lookback_years)
    ]
    subprocess.run(acquisition_cmd, check=True)
    
    # Step 2: Run feature engineering
    print("\nStep 2: Running feature engineering...")
    feature_cmd = [
        "python", "scripts/run_feature_engineering.py",
        "--input_path", f"{args.raw_dir}/market_data.csv",
        "--output_dir", args.features_dir
    ]
    subprocess.run(feature_cmd, check=True)
    
    print("\nPipeline completed successfully!")
    print(f"Raw data saved to: {args.raw_dir}/market_data.csv")
    print(f"Features saved to: {args.features_dir}/market_features.csv")

if __name__ == "__main__":
    main()