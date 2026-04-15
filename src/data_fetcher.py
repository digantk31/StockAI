"""
Data Fetcher Module
Handles fetching and preprocessing of historical stock data using yfinance
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from pathlib import Path

# Add project root to path for config imports
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from config.config import (
<<<<<<< HEAD
    STOCK_TICKERS, BENCHMARK_TICKER, BENCHMARK_TICKERS,
=======
    STOCK_TICKERS, BENCHMARK_TICKER, 
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
    START_DATE_STR, END_DATE_STR, DATA_DIR
)


class DataFetcher:
    """
    Class to fetch and preprocess stock market data
    """
    
<<<<<<< HEAD
    def __init__(self, tickers=None, start_date=None, end_date=None, benchmark=None):
=======
    def __init__(self, tickers=None, start_date=None, end_date=None):
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
        """
        Initialize DataFetcher with optional custom parameters
        
        Args:
            tickers: List of stock ticker symbols
            start_date: Start date for data (YYYY-MM-DD format)
            end_date: End date for data (YYYY-MM-DD format)
<<<<<<< HEAD
            benchmark: Custom benchmark ticker (auto-detected if None)
=======
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
        """
        self.tickers = tickers or STOCK_TICKERS
        self.start_date = start_date or START_DATE_STR
        self.end_date = end_date or END_DATE_STR
<<<<<<< HEAD
        self.benchmark = benchmark or self._detect_market_benchmark()
        self.price_data = None
        self.benchmark_data = None
    
    def _detect_market_benchmark(self):
        """
        Automatically detect the appropriate benchmark based on ticker patterns
        """
        if not self.tickers:
            return BENCHMARK_TICKER
            
        # Check ticker patterns to determine market
        indian_count = sum(1 for ticker in self.tickers if ticker.endswith('.NS'))
        us_count = sum(1 for ticker in self.tickers if '.' not in ticker and len(ticker) <= 5)
        european_count = sum(1 for ticker in self.tickers if any(ticker.endswith(suffix) for suffix in ['.L', '.DE', '.SW', '.AS', '.PA']))
        
        # Determine dominant market
        if indian_count >= max(us_count, european_count):
            return BENCHMARK_TICKERS.get('Indian', '^NSEI')
        elif european_count >= us_count:
            return BENCHMARK_TICKERS.get('European', '^STOXX50E')
        else:
            return BENCHMARK_TICKERS.get('US', '^GSPC')
=======
        self.benchmark = BENCHMARK_TICKER
        self.price_data = None
        self.benchmark_data = None
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
        
    def fetch_stock_data(self, save_to_csv=True):
        """
        Fetch historical adjusted close prices for all stocks
        
        Args:
            save_to_csv: Whether to save data to CSV file
            
        Returns:
            DataFrame with adjusted close prices for all stocks
        """
        print(f"Fetching stock data from {self.start_date} to {self.end_date}...")
        print(f"Stocks: {', '.join(self.tickers)}")
        
        # Download data for all tickers
        # auto_adjust=True often helps to get 'Close' that is actually adjusted
        data = yf.download(
            self.tickers,
            start=self.start_date,
            end=self.end_date,
            progress=True,
            auto_adjust=False  # Explicitly standard behavior
        )
        
        if data.empty:
            print("ERROR: No data fetched from yfinance.")
            self.price_data = pd.DataFrame()
            return self.price_data

        # Debug info
        # print(f"DEBUG: Downloaded data shape: {data.shape}")
        # print(f"DEBUG: Data columns levels: {data.columns.nlevels}")
        # if data.columns.nlevels > 0:
        #    print(f"DEBUG: Level 0: {data.columns.get_level_values(0).unique()}")
        
        # Handle different yfinance versions (newer versions use 'Close' instead of 'Adj Close')
        # Also handle multi-level columns from yfinance
        try:
            if isinstance(data.columns, pd.MultiIndex):
                # Multi-level columns: (Price Type, Ticker)
                # Check level 0 for price types
                level0 = data.columns.get_level_values(0)
                
                if 'Adj Close' in level0:
                    self.price_data = data['Adj Close']
                elif 'Close' in level0:
                    self.price_data = data['Close']
                else:
                    # Fallback: get the first level/group of columns if expected names not found
                    print("WARNING: Could not find 'Adj Close' or 'Close'. Using first available column group.")
                    # Assuming the structure is (PriceType, Ticker), we take the first price type
                    first_type = level0[0]
                    self.price_data = data[first_type]
            else:
                # Flat columns (rare for multiple tickers in new yfinance, but possible for single ticker)
                # If tickers are columns, it's just one price type (e.g. if we used auto_adjust=True usually)
                # But if we have (Adj Close, RELIANCE)... wait, that's handled by MultiIndex usually.
                # If it's just flat columns like ['RELIANCE.NS', 'TCS.NS'] then it IS the price data.
                
                # Check if columns are tickers or price types
                if 'Adj Close' in data.columns:
                    self.price_data = data[['Adj Close']] # Keep as DF
                elif 'Close' in data.columns:
                    self.price_data = data[['Close']]
                else:
                    # If columns intersect with tickers, assume it is already price data
                    if any(col in self.tickers for col in data.columns):
                        self.price_data = data
                    else:
                         self.price_data = data # Fallback

        except Exception as e:
            print(f"ERROR: Failed to parse data structure: {e}")
            # Last resort fallback
            self.price_data = data.iloc[:, :len(self.tickers)] # Guessing

        # Ensure self.price_data is a DataFrame
        if isinstance(self.price_data, pd.Series):
            self.price_data = self.price_data.to_frame()
            
        # Clean data
        self.price_data = self._clean_data(self.price_data)
        
        if save_to_csv and not self.price_data.empty:
            self._save_to_csv(self.price_data, "stock_prices.csv")
            
        print(f"Successfully fetched data for {len(self.price_data.columns)} stocks")
        if not self.price_data.empty:
            print(f"Date range: {self.price_data.index.min()} to {self.price_data.index.max()}")
            print(f"Total trading days: {len(self.price_data)}")
        else:
            print("WARNING: Data is empty after processing.")
        
        return self.price_data
    
    def fetch_benchmark_data(self, save_to_csv=True):
        """
        Fetch benchmark index (NIFTY 50) data
        
        Args:
            save_to_csv: Whether to save data to CSV file
            
        Returns:
            Series with benchmark adjusted close prices
        """
        print(f"\nFetching benchmark data ({self.benchmark})...")
        
        data = yf.download(
            self.benchmark,
            start=self.start_date,
            end=self.end_date,
            progress=True
        )
        
        # Handle different yfinance versions and column structures
        if isinstance(data.columns, pd.MultiIndex):
            # Multi-level columns
            if 'Close' in data.columns.get_level_values(0):
                self.benchmark_data = data['Close'].iloc[:, 0]
            else:
                self.benchmark_data = data.iloc[:, 0]
        else:
            # Single level columns
            if 'Adj Close' in data.columns:
                self.benchmark_data = data['Adj Close']
            elif 'Close' in data.columns:
                self.benchmark_data = data['Close']
            else:
                self.benchmark_data = data.iloc[:, 0]
        
        # Ensure it's a Series
        if isinstance(self.benchmark_data, pd.DataFrame):
            self.benchmark_data = self.benchmark_data.iloc[:, 0]
        
        self.benchmark_data.name = 'NIFTY50'
        
        # Clean data
        self.benchmark_data = self.benchmark_data.dropna()
        
        if save_to_csv:
            # Convert to DataFrame for saving
            benchmark_df = pd.DataFrame({'NIFTY50': self.benchmark_data})
            self._save_to_csv(benchmark_df, "benchmark_prices.csv")
            
        print(f"Successfully fetched benchmark data")
        
        return self.benchmark_data
    
    def _clean_data(self, data):
        """
        Clean and preprocess the data
        
        Args:
            data: Raw price DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if data.empty:
            return data
            
        # First, drop columns that are completely empty/NaN (e.g. failed downloads)
        data = data.dropna(axis=1, how='all')
        
        # Forward fill missing values (for holidays, etc.)
        data = data.ffill()
        
        # Backward fill any remaining NaN at the start
        data = data.bfill()
        
        # Drop any remaining rows with NaN
        data = data.dropna()
        
        # Sort by date
        data = data.sort_index()
        
        return data
    
    def _save_to_csv(self, data, filename):
        """
        Save data to CSV file
        
        Args:
            data: DataFrame to save
            filename: Name of the file
        """
        # Create data directory if it doesn't exist
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        filepath = os.path.join(DATA_DIR, filename)
        data.to_csv(filepath)
        print(f"Data saved to {filepath}")
    
    def get_stock_info(self, ticker):
        """
        Get detailed information about a stock
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        stock = yf.Ticker(ticker)
        return stock.info
    
    def get_all_data(self):
        """
        Fetch both stock and benchmark data
        
        Returns:
            Tuple of (stock_prices, benchmark_prices)
        """
        stock_data = self.fetch_stock_data()
        benchmark_data = self.fetch_benchmark_data()
        
        # Align dates
        common_dates = stock_data.index.intersection(benchmark_data.index)
        stock_data = stock_data.loc[common_dates]
        benchmark_data = benchmark_data.loc[common_dates]
        
        return stock_data, benchmark_data


if __name__ == "__main__":
    # Test the data fetcher
    fetcher = DataFetcher()
    stocks, benchmark = fetcher.get_all_data()
    
    print("\n" + "="*50)
    print("Stock Prices Summary:")
    print(stocks.describe())
    print("\nBenchmark Summary:")
    print(benchmark.describe())
