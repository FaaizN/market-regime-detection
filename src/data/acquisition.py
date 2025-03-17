# Data Fetching from APIs

import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta


class MarketDataFetcher:

    """
    This is a class to fetch financial data from Yahoo Finance.

    This will retrieve stock market data including prices, volumes,
    and derived indicators for analysis of market regimes.
    """

    def __init__(self, config=None):
        """
        Initialize the MarketDataFetcher wtih optimal config

        Param:
            Config (dict, optional): Configuration dictionary containing settings for data acquisition.
            Can include default tickers, time periods, etc.
        """

        self.config = config or {}

    def fetch_market_data(self, tickers, start_date, end_date = None):
        """
        Fetch market price data for a list of stock tickers
        
        Param:
            tickers (str): single ticker on list of symbols
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str, optional): End date in 'YYYY-MM-DD' format. If None uses Current data

        Returns:
            PD dataframe with market data (open, high, low, close etc.)
            indexed by date
        """

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # download market data with yfinance
        data = yf.download(tickers, start=start_date, end=end_date)
        return data
    
    def fetch_market_indices(self, indices = ['SPY', '^VIX', '^TNX'],start_date = None, lookback_years = 10):
        """
        Get market indices to serve as indicators

        Param:
            Indices (list): List of indices to get (SPY: S&P 500 ETF, ^VIX: Volatility Index, ^TNX: 10-year treasury yield)
            start_date (str, optional): start date in 'YYYY-MM-DD' format. If None uses lookback_years
            lookback_years (int, default = 10): number of years to lookback if start_date is None

        Returns:
            PD Dataframe containing index data indexed by date
        """

        if start_date is None:
            # Calculate the start date based on lookback_years
            start_date = (datetime.now() - timedelta(days=365*lookback_years)).strftime('%Y-%m-%d')

        # Get the indexed data
        index_data = self.fetch_market_data(indices, start_date)

        # Extract the Close prices
        if 'Close' in index_data.columns:
            return index_data['Close']
        else:
        # Handle MultiIndex columns case
            close_data = index_data.xs('Close', axis=1, level=0)
            return close_data
    
    def fetch_combined_dataset(self, market_tickers, index_tickers = None, start_date = None, lookback_years = 10):
        """
        Create a combined dataset of the stocks and market indices

        Params:
            market_tickers (str or list): stock ticker symbols to fetch
            index_tickers (list, optional): Index ticker symbols to fetch, if None uses default indices
            start_date (str, optional): start date in 'YYYY-MM-DD' format. If None uses lookback_years
            lookback_years (int, default = 10): number of years to lookback if the start_date is None

        Returns:
            PD Dataframe cobmined with market prices and index data. Indexed by date and missing values are removed.
        """

        if start_date is None:
            # Calculate start date based on lookback years if not provided
            start_date = (datetime.now() - timedelta(days=365*lookback_years)).strftime('%Y-%m-%d')
            
        # Use default tickers if none specified
        if index_tickers is None:
            index_tickers = ['SPY', '^VIX', '^TNX', '^GSPC', 'QQQ']

        # Get stock data
        market_data = self.fetch_market_data(market_tickers, start_date)

        # Get index data
        index_data = self.fetch_market_indices(index_tickers, start_date)

        # Extract the Close prices for simplicity
        if 'Close' in market_data.columns:
            market_data_close = market_data['Close']
        else:
            # Handle case where market_data has MultiIndex columns
            market_data_close = market_data.xs('Close', axis=1, level=0, drop_level=False)
        # Flatten the MultiIndex if needed
        if isinstance(market_data_close.columns, pd.MultiIndex):
            market_data_close.columns = market_data_close.columns.droplevel(0)

        # Combine the datasets horizontally 
        # Rename the index columns to make it clear they're indices
        index_data_renamed = index_data.rename(columns={col: f"IDX_{col}" for col in index_data.columns})

        combined = pd.concat([market_data_close, index_data_renamed], axis = 1)

        # Remove row with missing values
        return combined.dropna(how = 'all')
    

    def add_technical_indicators(self, data):
        """
        Add technical indicators to the dataset

        Params:
            data (PD dataframe): Dataframe containing price data

        Returns:
            PD Dataframe with added techinical indicators
        """

        # Create a copy to avoid modifying original data
        enhanced_data = data.copy()

        # Calculate the rolling averages
        for window in [5, 10, 20, 50, 200]:
            enhanced_data[f'MA_{window}'] = data.rolling(window = window).mean()

        # Calculate the volatility (std. dev)
        enhanced_data['Volatility_20'] = data.rolling(window = 20).std()

        # Calculate the return rates
        enhanced_data['Return_1D'] = data.pct_change(periods = 1)
        enhanced_data['Return_5D'] = data.pct_change(periods = 5)
        enhanced_data['Return_20D'] = data.pct_change(periods = 20)

        return enhanced_data
