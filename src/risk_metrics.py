"""
Risk Metrics Module
Calculates volatility, beta, Sharpe ratio, Sortino ratio and other risk measures
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from config.config import TRADING_DAYS, RISK_FREE_RATE


class RiskMetrics:
    """
    Class to calculate portfolio and individual stock risk metrics
    """
    
    def __init__(self, returns_data, benchmark_returns=None, risk_free_rate=None):
        """
        Initialize with returns data
        
        Args:
            returns_data: DataFrame with daily returns
            benchmark_returns: Series with benchmark daily returns
            risk_free_rate: Annual risk-free rate
        """
        self.returns = returns_data
        self.benchmark_returns = benchmark_returns
        self.risk_free_rate = risk_free_rate or RISK_FREE_RATE
        self.daily_rf = self.risk_free_rate / TRADING_DAYS
        
    def calculate_volatility(self, annualized=True):
        """
        Calculate volatility (standard deviation of returns)
        
        Args:
            annualized: Whether to annualize the volatility
            
        Returns:
            Series with volatility for each stock
        """
        vol = self.returns.std()
        
        if annualized:
            vol = vol * np.sqrt(TRADING_DAYS)
            
        return vol
    
    def calculate_variance(self, annualized=True):
        """
        Calculate variance of returns
        
        Args:
            annualized: Whether to annualize the variance
            
        Returns:
            Series with variance for each stock
        """
        var = self.returns.var()
        
        if annualized:
            var = var * TRADING_DAYS
            
        return var
    
    def calculate_beta(self):
        """
        Calculate beta (sensitivity to market)
        
        Formula: Beta = Cov(stock, market) / Var(market)
        
        Returns:
            Series with beta for each stock
        """
        if self.benchmark_returns is None:
            raise ValueError("Benchmark returns required to calculate beta")
        
        # Align data
        aligned_returns = self.returns.loc[self.benchmark_returns.index]
        
        betas = {}
        market_variance = self.benchmark_returns.var()
        
        for column in aligned_returns.columns:
            covariance = aligned_returns[column].cov(self.benchmark_returns)
            betas[column] = covariance / market_variance
            
        return pd.Series(betas)
    
    def calculate_alpha(self, expected_market_return=None):
        """
        Calculate Jensen's Alpha
        
        Formula: Alpha = R_p - [R_f + Beta * (R_m - R_f)]
        
        Returns:
            Series with alpha for each stock
        """
        if self.benchmark_returns is None:
            raise ValueError("Benchmark returns required to calculate alpha")
        
        betas = self.calculate_beta()
        
        # Annualized returns
        stock_returns = self.returns.mean() * TRADING_DAYS
        market_return = expected_market_return or (self.benchmark_returns.mean() * TRADING_DAYS)
        
        expected_returns = self.risk_free_rate + betas * (market_return - self.risk_free_rate)
        alphas = stock_returns - expected_returns
        
        return alphas
    
    def calculate_sharpe_ratio(self):
        """
        Calculate Sharpe Ratio
        
        Formula: Sharpe = (R_p - R_f) / sigma_p
        
        Returns:
            Series with Sharpe ratio for each stock
        """
        # Annualized excess returns
        excess_returns = self.returns.mean() * TRADING_DAYS - self.risk_free_rate
        
        # Annualized volatility
        volatility = self.calculate_volatility(annualized=True)
        
        return excess_returns / volatility
    
    def calculate_sortino_ratio(self):
        """
        Calculate Sortino Ratio (uses downside deviation)
        
        Formula: Sortino = (R_p - R_f) / sigma_d
        
        Returns:
            Series with Sortino ratio for each stock
        """
        # Calculate downside returns (negative returns only)
        downside_returns = self.returns[self.returns < 0]
        
        # Downside deviation
        downside_std = downside_returns.std() * np.sqrt(TRADING_DAYS)
        
        # Annualized excess returns
        excess_returns = self.returns.mean() * TRADING_DAYS - self.risk_free_rate
        
        return excess_returns / downside_std
    
    def calculate_treynor_ratio(self):
        """
        Calculate Treynor Ratio
        
        Formula: Treynor = (R_p - R_f) / Beta
        
        Returns:
            Series with Treynor ratio for each stock
        """
        betas = self.calculate_beta()
        excess_returns = self.returns.mean() * TRADING_DAYS - self.risk_free_rate
        
        return excess_returns / betas
    
    def calculate_information_ratio(self):
        """
        Calculate Information Ratio
        
        Formula: IR = (R_p - R_b) / Tracking Error
        
        Returns:
            Series with information ratio for each stock
        """
        if self.benchmark_returns is None:
            raise ValueError("Benchmark returns required")
        
        # Align data
        aligned_returns = self.returns.loc[self.benchmark_returns.index]
        
        excess_returns = aligned_returns.subtract(self.benchmark_returns, axis=0)
        
        # Annualized
        mean_excess = excess_returns.mean() * TRADING_DAYS
        tracking_error = excess_returns.std() * np.sqrt(TRADING_DAYS)
        
        return mean_excess / tracking_error
    
    def calculate_tracking_error(self):
        """
        Calculate Tracking Error (standard deviation of excess returns)
        
        Returns:
            Series with tracking error for each stock
        """
        if self.benchmark_returns is None:
            raise ValueError("Benchmark returns required")
        
        aligned_returns = self.returns.loc[self.benchmark_returns.index]
        excess_returns = aligned_returns.subtract(self.benchmark_returns, axis=0)
        
        return excess_returns.std() * np.sqrt(TRADING_DAYS)
    
    def calculate_max_drawdown(self):
        """
        Calculate Maximum Drawdown
        
        Formula: MDD = (Peak - Trough) / Peak
        
        Returns:
            Series with max drawdown for each stock
        """
        # Calculate cumulative returns
        cumulative = (1 + self.returns).cumprod()
        
        # Rolling maximum
        running_max = cumulative.cummax()
        
        # Drawdown
        drawdown = (cumulative - running_max) / running_max
        
        # Maximum drawdown
        max_drawdown = drawdown.min()
        
        return max_drawdown
    
    def calculate_calmar_ratio(self):
        """
        Calculate Calmar Ratio (return / max drawdown)
        
        Returns:
            Series with Calmar ratio for each stock
        """
        annualized_return = self.returns.mean() * TRADING_DAYS
        max_dd = abs(self.calculate_max_drawdown())
        
        return annualized_return / max_dd
    
    def calculate_portfolio_risk(self, weights):
        """
        Calculate portfolio volatility given weights
        
        Args:
            weights: Array of portfolio weights
            
        Returns:
            Portfolio volatility (annualized)
        """
        weights = np.array(weights)
        cov_matrix = self.returns.cov() * TRADING_DAYS
        
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        return portfolio_volatility
    
    def get_risk_summary(self):
        """
        Get comprehensive risk metrics summary
        
        Returns:
            DataFrame with all risk metrics
        """
        summary = pd.DataFrame({
            'Volatility (%)': self.calculate_volatility(annualized=True) * 100,
            'Beta': self.calculate_beta() if self.benchmark_returns is not None else None,
            'Sharpe Ratio': self.calculate_sharpe_ratio(),
            'Sortino Ratio': self.calculate_sortino_ratio(),
            'Max Drawdown (%)': self.calculate_max_drawdown() * 100,
            'Calmar Ratio': self.calculate_calmar_ratio(),
        })
        
        if self.benchmark_returns is not None:
            summary['Alpha (%)'] = self.calculate_alpha() * 100
            summary['Information Ratio'] = self.calculate_information_ratio()
            summary['Tracking Error (%)'] = self.calculate_tracking_error() * 100
        
        return summary.round(4)
    
    def get_summary_table(self):
        """
        Alias for get_risk_summary for API consistency
        """
        return self.get_risk_summary()


if __name__ == "__main__":
    # Test risk metrics
    from data_fetcher import DataFetcher
    from returns_analysis import ReturnsAnalysis
    
    fetcher = DataFetcher()
    prices, benchmark = fetcher.get_all_data()
    
    returns_analyzer = ReturnsAnalysis(prices)
    daily_returns = returns_analyzer.calculate_daily_returns()
    
    benchmark_returns = benchmark.pct_change().dropna()
    
    risk_metrics = RiskMetrics(daily_returns, benchmark_returns)
    
    print("\n" + "="*60)
    print("Risk Metrics Summary")
    print("="*60)
    print(risk_metrics.get_risk_summary())
