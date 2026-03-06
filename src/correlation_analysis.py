"""
Correlation Analysis Module
Analyzes correlation between stocks for diversification assessment
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


class CorrelationAnalysis:
    """
    Class to analyze correlations and diversification benefits
    """
    
    def __init__(self, returns_data):
        """
        Initialize with returns data
        
        Args:
            returns_data: DataFrame with daily returns
        """
        self.returns = returns_data
        self.correlation_matrix = None
        self.covariance_matrix = None
        
    def calculate_correlation_matrix(self):
        """
        Calculate correlation matrix between all stocks
        
        Returns:
            DataFrame with correlation coefficients
        """
        self.correlation_matrix = self.returns.corr()
        return self.correlation_matrix
    
    def calculate_covariance_matrix(self, annualized=True):
        """
        Calculate covariance matrix between all stocks
        
        Args:
            annualized: Whether to annualize the covariance
            
        Returns:
            DataFrame with covariance values
        """
        self.covariance_matrix = self.returns.cov()
        
        if annualized:
            self.covariance_matrix = self.covariance_matrix * 252
            
        return self.covariance_matrix
    
    def get_pairwise_correlations(self):
        """
        Get all pairwise correlations sorted by value
        
        Returns:
            DataFrame with stock pairs and their correlations
        """
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        # Get upper triangle of correlation matrix
        mask = np.triu(np.ones_like(self.correlation_matrix, dtype=bool), k=1)
        
        pairs = []
        for i in range(len(self.correlation_matrix.columns)):
            for j in range(i+1, len(self.correlation_matrix.columns)):
                pairs.append({
                    'Stock 1': self.correlation_matrix.columns[i],
                    'Stock 2': self.correlation_matrix.columns[j],
                    'Correlation': self.correlation_matrix.iloc[i, j]
                })
        
        pairs_df = pd.DataFrame(pairs)
        pairs_df = pairs_df.sort_values('Correlation', ascending=False)
        
        return pairs_df.reset_index(drop=True)
    
    def get_highest_correlations(self, n=5):
        """
        Get the n highest correlated stock pairs
        
        Args:
            n: Number of pairs to return
            
        Returns:
            DataFrame with most correlated pairs
        """
        pairs = self.get_pairwise_correlations()
        return pairs.head(n)
    
    def get_lowest_correlations(self, n=5):
        """
        Get the n lowest correlated stock pairs (best for diversification)
        
        Args:
            n: Number of pairs to return
            
        Returns:
            DataFrame with least correlated pairs
        """
        pairs = self.get_pairwise_correlations()
        return pairs.tail(n)
    
    def calculate_average_correlation(self):
        """
        Calculate average correlation across all pairs
        
        Returns:
            Float with average correlation
        """
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        # Get upper triangle values (excluding diagonal)
        mask = np.triu(np.ones_like(self.correlation_matrix, dtype=bool), k=1)
        upper_values = self.correlation_matrix.where(mask).stack()
        
        return upper_values.mean()
    
    def calculate_diversification_ratio(self, weights):
        """
        Calculate portfolio diversification ratio
        
        Diversification Ratio = Weighted Average Vol / Portfolio Vol
        Higher ratio indicates better diversification
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Diversification ratio
        """
        weights = np.array(weights)
        
        # Individual volatilities
        individual_vols = self.returns.std() * np.sqrt(252)
        
        # Weighted average volatility
        weighted_avg_vol = np.dot(weights, individual_vols)
        
        # Portfolio volatility
        cov_matrix = self.returns.cov() * 252
        portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_vol = np.sqrt(portfolio_var)
        
        return weighted_avg_vol / portfolio_vol
    
    def calculate_concentration_ratio(self, weights, n=3):
        """
        Calculate portfolio concentration (sum of top n weights)
        
        Args:
            weights: Portfolio weights
            n: Number of top holdings to consider
            
        Returns:
            Concentration ratio (0-1)
        """
        sorted_weights = np.sort(weights)[::-1]
        return np.sum(sorted_weights[:n])
    
    def calculate_herfindahl_index(self, weights):
        """
        Calculate Herfindahl-Hirschman Index for portfolio concentration
        
        HHI = sum of squared weights
        Range: 1/n (fully diversified) to 1 (single stock)
        
        Args:
            weights: Portfolio weights
            
        Returns:
            HHI value
        """
        weights = np.array(weights)
        return np.sum(weights ** 2)
    
    def calculate_effective_number_of_stocks(self, weights):
        """
        Calculate effective number of stocks in portfolio
        
        ENS = 1 / HHI
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Effective number of stocks
        """
        hhi = self.calculate_herfindahl_index(weights)
        return 1 / hhi
    
    def get_correlation_clusters(self, threshold=0.7):
        """
        Identify clusters of highly correlated stocks
        
        Args:
            threshold: Correlation threshold for clustering
            
        Returns:
            List of correlated stock groups
        """
        if self.correlation_matrix is None:
            self.calculate_correlation_matrix()
        
        clusters = []
        visited = set()
        
        for stock in self.correlation_matrix.columns:
            if stock not in visited:
                # Find all stocks correlated above threshold
                correlated = self.correlation_matrix[stock][
                    self.correlation_matrix[stock] > threshold
                ].index.tolist()
                
                if len(correlated) > 1:
                    clusters.append(correlated)
                    visited.update(correlated)
        
        return clusters
    
    def get_diversification_summary(self, weights):
        """
        Get comprehensive diversification metrics
        
        Args:
            weights: Portfolio weights
            
        Returns:
            Dictionary with diversification metrics
        """
        weights = np.array(weights)
        
        return {
            'Average Correlation': self.calculate_average_correlation(),
            'Diversification Ratio': self.calculate_diversification_ratio(weights),
            'HHI Index': self.calculate_herfindahl_index(weights),
            'Effective # of Stocks': self.calculate_effective_number_of_stocks(weights),
            'Top 3 Concentration': self.calculate_concentration_ratio(weights, 3),
            'Correlation Clusters (>0.7)': self.get_correlation_clusters(0.7)
        }


if __name__ == "__main__":
    # Test correlation analysis
    from data_fetcher import DataFetcher
    from returns_analysis import ReturnsAnalysis
    
    fetcher = DataFetcher()
    prices, _ = fetcher.get_all_data()
    
    returns_analyzer = ReturnsAnalysis(prices)
    daily_returns = returns_analyzer.calculate_daily_returns()
    
    corr_analyzer = CorrelationAnalysis(daily_returns)
    
    print("\n" + "="*60)
    print("Correlation Matrix")
    print("="*60)
    print(corr_analyzer.calculate_correlation_matrix().round(2))
    
    print("\n" + "="*60)
    print("Highest Correlations")
    print("="*60)
    print(corr_analyzer.get_highest_correlations())
    
    print("\n" + "="*60)
    print("Lowest Correlations (Best for Diversification)")
    print("="*60)
    print(corr_analyzer.get_lowest_correlations())
