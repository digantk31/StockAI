"""
Returns Analysis Module
Calculates daily, monthly, annual returns and CAGR
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from config.config import TRADING_DAYS


class ReturnsAnalysis:
    """
    Class to calculate and analyze investment returns
    """
    
    def __init__(self, price_data):
        """
        Initialize with price data
        
        Args:
            price_data: DataFrame with stock prices (Date index, stock columns)
        """
        self.price_data = price_data
        self.daily_returns = None
        self.monthly_returns = None
        self.annual_returns = None
        
    def calculate_daily_returns(self):
        """
        Calculate daily percentage returns
        
        Formula: r_t = (P_t - P_{t-1}) / P_{t-1}
        
        Returns:
            DataFrame with daily returns
        """
        self.daily_returns = self.price_data.pct_change().dropna()
        return self.daily_returns
    
    def calculate_log_returns(self):
        """
        Calculate daily logarithmic returns
        
        Formula: r_t = ln(P_t / P_{t-1})
        
        Returns:
            DataFrame with log returns
        """
        return np.log(self.price_data / self.price_data.shift(1)).dropna()
    
    def calculate_monthly_returns(self):
        """
        Calculate monthly returns by resampling
        
        Returns:
            DataFrame with monthly returns
        """
        # Resample to month-end prices (using 'ME' for newer pandas versions)
        monthly_prices = self.price_data.resample('ME').last()
        self.monthly_returns = monthly_prices.pct_change().dropna()
        return self.monthly_returns
    
    def calculate_annual_returns(self):
        """
        Calculate annual returns by resampling
        
        Returns:
            DataFrame with annual returns
        """
        # Resample to year-end prices (using 'YE' for newer pandas versions)
        annual_prices = self.price_data.resample('YE').last()
        self.annual_returns = annual_prices.pct_change().dropna()
        return self.annual_returns
    
    def calculate_cagr(self):
        """
        Calculate Compound Annual Growth Rate for each stock
        
        Formula: CAGR = (P_end / P_start)^(1/n) - 1
        
        Returns:
            Series with CAGR for each stock
        """
        start_prices = self.price_data.iloc[0]
        end_prices = self.price_data.iloc[-1]
        
        # Calculate number of years
        days = (self.price_data.index[-1] - self.price_data.index[0]).days
        years = days / 365.25
        
        cagr = (end_prices / start_prices) ** (1 / years) - 1
        return cagr
    
    def calculate_cumulative_returns(self):
        """
        Calculate cumulative returns over time
        
        Returns:
            DataFrame with cumulative returns
        """
        if self.daily_returns is None:
            self.calculate_daily_returns()
            
        cumulative = (1 + self.daily_returns).cumprod() - 1
        return cumulative
    
    def calculate_total_return(self):
        """
        Calculate total return over the entire period
        
        Returns:
            Series with total return for each stock
        """
        return (self.price_data.iloc[-1] / self.price_data.iloc[0]) - 1
    
    def calculate_portfolio_returns(self, weights):
        """
        Calculate portfolio returns given weights
        
        Args:
            weights: List or array of portfolio weights
            
        Returns:
            Series with portfolio daily returns
        """
        if self.daily_returns is None:
            self.calculate_daily_returns()
            
        weights = np.array(weights)
        portfolio_returns = (self.daily_returns * weights).sum(axis=1)
        return portfolio_returns
    
    def calculate_rolling_returns(self, window=21):
        """
        Calculate rolling returns over a specified window
        
        Args:
            window: Rolling window size in days (default 21 for monthly)
            
        Returns:
            DataFrame with rolling returns
        """
        return self.price_data.pct_change(periods=window).dropna()
    
    def get_returns_statistics(self):
        """
        Get comprehensive statistics for all return types
        
        Returns:
            Dictionary with return statistics
        """
        if self.daily_returns is None:
            self.calculate_daily_returns()
        if self.monthly_returns is None:
            self.calculate_monthly_returns()
        if self.annual_returns is None:
            self.calculate_annual_returns()
            
        stats = {
            'daily_mean': self.daily_returns.mean(),
            'daily_std': self.daily_returns.std(),
            'monthly_mean': self.monthly_returns.mean(),
            'monthly_std': self.monthly_returns.std(),
            'annual_mean': self.annual_returns.mean() if len(self.annual_returns) > 0 else None,
            'annual_std': self.annual_returns.std() if len(self.annual_returns) > 0 else None,
            'cagr': self.calculate_cagr(),
            'total_return': self.calculate_total_return(),
            'annualized_return': self.daily_returns.mean() * TRADING_DAYS,
            'annualized_volatility': self.daily_returns.std() * np.sqrt(TRADING_DAYS)
        }
        
        return stats
    
    def get_summary_table(self):
        """
        Create a summary table of all return metrics
        
        Returns:
            DataFrame with summary statistics
        """
        stats = self.get_returns_statistics()
        
        summary = pd.DataFrame({
            'CAGR (%)': stats['cagr'] * 100,
            'Total Return (%)': stats['total_return'] * 100,
            'Annualized Return (%)': stats['annualized_return'] * 100,
            'Annualized Volatility (%)': stats['annualized_volatility'] * 100,
            'Daily Mean (%)': stats['daily_mean'] * 100,
            'Daily Std (%)': stats['daily_std'] * 100,
        })
        
        return summary.round(2)


if __name__ == "__main__":
    # Test returns analysis
    from data_fetcher import DataFetcher
    
    fetcher = DataFetcher()
    prices, _ = fetcher.get_all_data()
    
    analyzer = ReturnsAnalysis(prices)
    
    print("\n" + "="*60)
    print("Returns Analysis Summary")
    print("="*60)
    print(analyzer.get_summary_table())
