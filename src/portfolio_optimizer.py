"""
Portfolio Optimizer Module
Implements Mean-Variance Optimization and Efficient Frontier generation
"""
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
from config.config import TRADING_DAYS, RISK_FREE_RATE


class PortfolioOptimizer:
    """
    Class to perform portfolio optimization using Modern Portfolio Theory
    """
    
    def __init__(self, returns_data, risk_free_rate=None):
        """
        Initialize with returns data
        
        Args:
            returns_data: DataFrame with daily returns
            risk_free_rate: Annual risk-free rate
        """
        self.returns = returns_data
        self.risk_free_rate = risk_free_rate or RISK_FREE_RATE
        self.n_assets = len(returns_data.columns)
        self.assets = returns_data.columns.tolist()
        
        # Calculate expected returns and covariance
        self.expected_returns = self._calculate_expected_returns()
        self.cov_matrix = self._calculate_covariance()
        
    def _calculate_expected_returns(self):
        """
        Calculate annualized expected returns for each asset
        
        Returns:
            Array of expected returns
        """
        return self.returns.mean() * TRADING_DAYS
    
    def _calculate_covariance(self):
        """
        Calculate annualized covariance matrix
        
        Returns:
            Covariance matrix
        """
        return self.returns.cov() * TRADING_DAYS
    
    def _portfolio_return(self, weights):
        """
        Calculate portfolio return
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Expected portfolio return
        """
        return np.dot(weights, self.expected_returns)
    
    def _portfolio_volatility(self, weights):
        """
        Calculate portfolio volatility
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Portfolio standard deviation
        """
        return np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
    
    def _negative_sharpe_ratio(self, weights):
        """
        Calculate negative Sharpe ratio (for minimization)
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Negative Sharpe ratio
        """
        ret = self._portfolio_return(weights)
        vol = self._portfolio_volatility(weights)
        return -(ret - self.risk_free_rate) / vol
    
    def optimize_sharpe_ratio(self):
        """
        Find the portfolio with maximum Sharpe ratio
        
        Returns:
            Dict with optimal weights, return, volatility, and Sharpe ratio
        """
        # Initial guess (equal weights)
        init_weights = np.array([1/self.n_assets] * self.n_assets)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
        ]
        
        # Bounds (no short selling)
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Optimize
        result = minimize(
            self._negative_sharpe_ratio,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        optimal_return = self._portfolio_return(optimal_weights)
        optimal_volatility = self._portfolio_volatility(optimal_weights)
        optimal_sharpe = (optimal_return - self.risk_free_rate) / optimal_volatility
        
        return {
            'weights': dict(zip(self.assets, optimal_weights)),
            'return': optimal_return,
            'volatility': optimal_volatility,
            'sharpe_ratio': optimal_sharpe
        }
    
    def optimize_min_volatility(self):
        """
        Find the minimum volatility portfolio
        
        Returns:
            Dict with optimal weights, return, volatility
        """
        # Initial guess
        init_weights = np.array([1/self.n_assets] * self.n_assets)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Optimize
        result = minimize(
            self._portfolio_volatility,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        optimal_return = self._portfolio_return(optimal_weights)
        optimal_volatility = self._portfolio_volatility(optimal_weights)
        
        return {
            'weights': dict(zip(self.assets, optimal_weights)),
            'return': optimal_return,
            'volatility': optimal_volatility,
            'sharpe_ratio': (optimal_return - self.risk_free_rate) / optimal_volatility
        }
    
    def optimize_target_return(self, target_return):
        """
        Find minimum volatility portfolio for a target return
        
        Args:
            target_return: Desired portfolio return
            
        Returns:
            Dict with optimal weights, return, volatility
        """
        # Initial guess
        init_weights = np.array([1/self.n_assets] * self.n_assets)
        
        # Constraints
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: self._portfolio_return(w) - target_return}
        ]
        
        # Bounds
        bounds = tuple((0, 1) for _ in range(self.n_assets))
        
        # Optimize
        result = minimize(
            self._portfolio_volatility,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            return None
        
        optimal_weights = result.x
        optimal_volatility = self._portfolio_volatility(optimal_weights)
        
        return {
            'weights': dict(zip(self.assets, optimal_weights)),
            'return': target_return,
            'volatility': optimal_volatility,
            'sharpe_ratio': (target_return - self.risk_free_rate) / optimal_volatility
        }
    
    def generate_efficient_frontier(self, n_portfolios=100):
        """
        Generate the efficient frontier
        
        Args:
            n_portfolios: Number of portfolios on the frontier
            
        Returns:
            DataFrame with frontier portfolios
        """
        # Get min and max return from current assets
        min_vol_portfolio = self.optimize_min_volatility()
        max_sharpe_portfolio = self.optimize_sharpe_ratio()
        
        min_return = min_vol_portfolio['return']
        max_return = max(self.expected_returns)
        
        # Generate target returns
        target_returns = np.linspace(min_return, max_return, n_portfolios)
        
        frontier = []
        for target in target_returns:
            result = self.optimize_target_return(target)
            if result is not None:
                frontier.append({
                    'Return': result['return'],
                    'Volatility': result['volatility'],
                    'Sharpe Ratio': result['sharpe_ratio'],
                    **{f'Weight_{asset}': result['weights'].get(asset, 0) 
                       for asset in self.assets}
                })
        
        return pd.DataFrame(frontier)
    
    def generate_random_portfolios(self, n_portfolios=5000):
        """
        Generate random portfolios for Monte Carlo simulation
        
        Args:
            n_portfolios: Number of random portfolios
            
        Returns:
            DataFrame with portfolio statistics
        """
        results = []
        
        for _ in range(n_portfolios):
            # Generate random weights
            weights = np.random.random(self.n_assets)
            weights = weights / np.sum(weights)  # Normalize to sum to 1
            
            ret = self._portfolio_return(weights)
            vol = self._portfolio_volatility(weights)
            sharpe = (ret - self.risk_free_rate) / vol
            
            results.append({
                'Return': ret,
                'Volatility': vol,
                'Sharpe Ratio': sharpe,
                **{f'Weight_{asset}': w for asset, w in zip(self.assets, weights)}
            })
        
        return pd.DataFrame(results)
    
    def get_equal_weight_portfolio(self):
        """
        Get equal-weighted portfolio statistics
        
        Returns:
            Dict with portfolio statistics
        """
        weights = np.array([1/self.n_assets] * self.n_assets)
        
        return {
            'weights': dict(zip(self.assets, weights)),
            'return': self._portfolio_return(weights),
            'volatility': self._portfolio_volatility(weights),
            'sharpe_ratio': (self._portfolio_return(weights) - self.risk_free_rate) / 
                           self._portfolio_volatility(weights)
        }
    
    def get_optimization_summary(self):
        """
        Get summary of all optimization results
        
        Returns:
            DataFrame with optimization summary
        """
        max_sharpe = self.optimize_sharpe_ratio()
        min_vol = self.optimize_min_volatility()
        equal_weight = self.get_equal_weight_portfolio()
        
        summary = pd.DataFrame({
            'Max Sharpe': {
                'Return (%)': max_sharpe['return'] * 100,
                'Volatility (%)': max_sharpe['volatility'] * 100,
                'Sharpe Ratio': max_sharpe['sharpe_ratio'],
                **{k: v * 100 for k, v in max_sharpe['weights'].items()}
            },
            'Min Volatility': {
                'Return (%)': min_vol['return'] * 100,
                'Volatility (%)': min_vol['volatility'] * 100,
                'Sharpe Ratio': min_vol['sharpe_ratio'],
                **{k: v * 100 for k, v in min_vol['weights'].items()}
            },
            'Equal Weight': {
                'Return (%)': equal_weight['return'] * 100,
                'Volatility (%)': equal_weight['volatility'] * 100,
                'Sharpe Ratio': equal_weight['sharpe_ratio'],
                **{k: v * 100 for k, v in equal_weight['weights'].items()}
            }
        })
        
        return summary.round(2)


if __name__ == "__main__":
    # Test portfolio optimizer
    from data_fetcher import DataFetcher
    from returns_analysis import ReturnsAnalysis
    
    fetcher = DataFetcher()
    prices, _ = fetcher.get_all_data()
    
    returns_analyzer = ReturnsAnalysis(prices)
    daily_returns = returns_analyzer.calculate_daily_returns()
    
    optimizer = PortfolioOptimizer(daily_returns)
    
    print("\n" + "="*60)
    print("Portfolio Optimization Results")
    print("="*60)
    
    max_sharpe = optimizer.optimize_sharpe_ratio()
    print("\nMaximum Sharpe Ratio Portfolio:")
    print(f"Expected Return: {max_sharpe['return']*100:.2f}%")
    print(f"Volatility: {max_sharpe['volatility']*100:.2f}%")
    print(f"Sharpe Ratio: {max_sharpe['sharpe_ratio']:.4f}")
    print("\nOptimal Weights:")
    for asset, weight in max_sharpe['weights'].items():
        if weight > 0.01:  # Show only weights > 1%
            print(f"  {asset}: {weight*100:.2f}%")
    
    min_vol = optimizer.optimize_min_volatility()
    print("\n\nMinimum Volatility Portfolio:")
    print(f"Expected Return: {min_vol['return']*100:.2f}%")
    print(f"Volatility: {min_vol['volatility']*100:.2f}%")
    print(f"Sharpe Ratio: {min_vol['sharpe_ratio']:.4f}")
