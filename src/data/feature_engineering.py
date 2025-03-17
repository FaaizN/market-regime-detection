import pandas as pd
import numpy as np

class FeatureEngineer:

    """
    Class for creating features from market data for regime detection
    """

    def __init__(self, config = None):
        """
        Initialize the feautre engineer with optional configuration

        """

        self.config = config or {}

    def calculate_technical_indicators(self, data):
        """
        Calculate technical indicators from price data

        Params:
            data (PD Dataframe): Contains price data for various assets

        Returns:
            PD Dataframe with technical indicators added
        """

        result = data.copy()

        # For each asset in the dataset
        for column in data.columns:
            # Skip the columns that are derived
            if column.startswith('IDX_') or '_' in column:
                continue

            # Calculate the moving averages
            for window in [5, 10, 20, 50, 200]:
                result[f'{column}_MA_{window}'] = data[column].rolling(window = window).mean()

            # Calculate the volatility
            result[f'{column}_VOLATILITY_20'] = data[column].rolling(window = 20).std()

            # Calculate the momentum
            result[f'{column}_MOM_20'] = data[column].pct_change(periods = 20)

            # Calcualte the RSI
            delta = data[column].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window = 14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window = 14).mean()
            rs = gain / loss
            result[f'{column}_RSI_14'] = 100 - (100 / (1 + rs))

        return result
    
    def calculate_market_features(self, data):
        """
        Calculate market-wide features

        Params:
            data (PD Dataframe): Contains price data for multiple assets

        Returns:
            PD Dataframe with market features added
        """

        result = data.copy()

        # Use only actual stock columns, not indices or derived columns
        stock_columns = [col for col in data.columns if not (col.startswith('IDX_') or '_' in col)]

        if len(stock_columns) > 0:
            # Calculate avg returns
            stock_returns = data[stock_columns].pct_change()
            result['MARKET_MEAN_RETURN'] = stock_returns.mean(axis = 1)

            # Calculate the market volatility
            result['MARKET_VOLATILITY'] = stock_returns.std(axis = 1)

            # Calculate percentage of stocks above their 50-day MA
            above_ma = pd.DataFrame()
            for col in stock_columns:
                if f'{col}_MA_50' in result.columns:
                    above_ma[col] = result[col] > result[f'{col}_MA_50']

            if not above_ma.empty:
                result['MARKET_PERCENT_ABOVE_MA'] = above_ma.mean(axis = 1) * 100

        return result
    
    def create_regime_features(self, data, vix_column = 'IDX_^VIX'):
        """
        Create specific features for regime detection

        Params:
            data (PD Dataframe): Data containing price and technical indicator data
            vix_column (str, optional): column name for VIX data

        Returns:
            PD Dataframe with regime detection features
        """

        result = data.copy()

        # Get the SPY column
        spy_column = next((col for col in data.columns if col == 'IDX_SPY'), None)

        if spy_column and vix_column in data.columns:
            # Calculate the SPY trend
            result['SPY_TREND'] = result[spy_column].pct_change(periods = 20)

            # Calculate the VIX trend
            result['VIX_TREND'] = result[vix_column].pct_change(periods = 10)

            # Calculate the SPY/VIX ratio 
            result['SPY_VIX_RATIO'] = result[spy_column] / result[vix_column]

            # Calculate the rolling correlations between SPY and VIX
            result['SPY_VIX_CORR_20'] = result[spy_column].rolling(20).corr(result[vix_column])

        return result
    
    def process_data(self, data):
        """
        Process the data through the full feature engineering pipeline

        Params:
            Data (PD Dataframe): Raw market data

        Returns:
            PD Dataframe with processed market data and all features
        """

        # Calculate the technical indicators
        data_with_indicators = self.calculate_technical_indicators(data)

        # Calculate the market features
        data_with_market = self.calculate_market_features(data_with_indicators)

        # Calculate the regime features
        full_data = self.create_regime_features(data_with_market)

        # Drop the NA values
        cleaned_data = full_data.dropna()

        return cleaned_data