"""
Backtesting Engine with Transaction Costs
Comprehensive backtesting framework with realistic trading simulation
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px
from enum import Enum

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class TransactionCost:
    """Transaction cost configuration"""
    brokerage_fee: float = 0.0001  # 0.01% per trade
    stt_tax: float = 0.0006        # 0.06% STT (India)
    other_charges: float = 0.0001  # Other regulatory charges
    slippage: float = 0.0005       # 0.05% slippage
    min_brokerage: float = 25.0    # Minimum brokerage fee
    
    def calculate_total_cost(self, trade_value: float) -> float:
        """Calculate total transaction cost for a trade"""
        brokerage = max(self.brokerage_fee * trade_value, self.min_brokerage)
        stt = self.stt_tax * trade_value if trade_value > 0 else 0
        other = self.other_charges * trade_value
        slippage_cost = self.slippage * trade_value
        
        return brokerage + stt + other + slippage_cost

@dataclass
class Trade:
    """Trade execution record"""
    timestamp: datetime
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    trade_value: float
    transaction_cost: float
    net_value: float
    order_type: OrderType
    portfolio_value_before: float
    portfolio_value_after: float

@dataclass
class Position:
    """Current position in a stock"""
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float

class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> Dict[str, str]:
        """
        Generate trading signals
        
        Args:
            data: Historical price data
            timestamp: Current timestamp
            
        Returns:
            Dict mapping symbols to signals ('buy', 'sell', 'hold')
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, symbol: str, signal: str, portfolio_value: float, 
                              current_positions: Dict[str, Position]) -> int:
        """Calculate position size based on risk management"""
        pass

class BacktestEngine:
    """
    Comprehensive backtesting engine with transaction costs
    """
    
    def __init__(self, initial_capital: float = 100000, transaction_cost: TransactionCost = None):
        """
        Initialize backtesting engine
        
        Args:
            initial_capital: Starting capital for backtest
            transaction_cost: Transaction cost configuration
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.transaction_cost = transaction_cost or TransactionCost()
        
        # Portfolio tracking
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.portfolio_values: List[Tuple[datetime, float]] = []
        self.cash = initial_capital
        
        # Performance tracking
        self.daily_returns: List[float] = []
        self.equity_curve: List[float] = []
        
    def add_data(self, symbol: str, data: pd.DataFrame):
        """Add historical data for a symbol"""
        if not hasattr(self, 'data'):
            self.data = {}
        self.data[symbol] = data
        
    def execute_trade(self, symbol: str, side: OrderSide, quantity: int, 
                     price: float, timestamp: datetime, order_type: OrderType = OrderType.MARKET) -> bool:
        """
        Execute a trade with transaction costs
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            quantity: Number of shares
            price: Execution price
            timestamp: Trade timestamp
            order_type: Type of order
            
        Returns:
            bool: True if trade executed successfully
        """
        trade_value = quantity * price
        transaction_cost = self.transaction_cost.calculate_total_cost(trade_value)
        net_value = trade_value + transaction_cost
        
        # Check if we have enough cash for buy orders
        if side == OrderSide.BUY and net_value > self.cash:
            return False
            
        # Check if we have enough shares for sell orders
        if side == OrderSide.SELL:
            if symbol not in self.positions or self.positions[symbol].quantity < quantity:
                return False
                
        portfolio_value_before = self.calculate_portfolio_value(timestamp)
        
        # Execute trade
        if side == OrderSide.BUY:
            self.cash -= net_value
            
            if symbol not in self.positions:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=0,
                    avg_price=0,
                    current_price=price,
                    unrealized_pnl=0,
                    realized_pnl=0
                )
                
            # Update position
            old_quantity = self.positions[symbol].quantity
            old_avg_price = self.positions[symbol].avg_price
            new_quantity = old_quantity + quantity
            new_avg_price = ((old_quantity * old_avg_price) + (quantity * price)) / new_quantity
            
            self.positions[symbol].quantity = new_quantity
            self.positions[symbol].avg_price = new_avg_price
            self.positions[symbol].current_price = price
            
        else:  # SELL
            self.cash += net_value - transaction_cost  # Add proceeds minus costs
            
            # Update position
            if symbol in self.positions:
                old_quantity = self.positions[symbol].quantity
                old_avg_price = self.positions[symbol].avg_price
                
                # Calculate realized PnL
                realized_pnl = (price - old_avg_price) * quantity
                self.positions[symbol].realized_pnl += realized_pnl
                self.positions[symbol].quantity -= quantity
                
                # Remove position if no shares left
                if self.positions[symbol].quantity == 0:
                    del self.positions[symbol]
                    
        portfolio_value_after = self.calculate_portfolio_value(timestamp)
        
        # Record trade
        trade = Trade(
            timestamp=timestamp,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            trade_value=trade_value,
            transaction_cost=transaction_cost,
            net_value=net_value,
            order_type=order_type,
            portfolio_value_before=portfolio_value_before,
            portfolio_value_after=portfolio_value_after
        )
        
        self.trades.append(trade)
        return True
        
    def calculate_portfolio_value(self, timestamp: datetime) -> float:
        """Calculate total portfolio value including cash and positions"""
        total_value = self.cash
        
        for symbol, position in self.positions.items():
            if symbol in self.data:
                # Fix Series ambiguity by using boolean indexing properly
                symbol_data = self.data[symbol]
                valid_data = symbol_data[symbol_data.index <= timestamp]
                
                if not valid_data.empty:
                    close_data = valid_data['Close']
                    if isinstance(close_data, pd.Series):
                        current_price = close_data.iloc[-1]
                    else:
                        current_price = close_data.iloc[-1, 0] if len(close_data.columns) > 0 else close_data.iloc[-1]
                    
                    position.current_price = current_price
                    position.unrealized_pnl = (current_price - position.avg_price) * position.quantity
                    total_value += position.quantity * current_price
                
        return total_value
        
    def run_backtest(self, strategy: TradingStrategy, start_date: datetime, end_date: datetime) -> Dict:
        """
        Run backtest with given strategy
        
        Args:
            strategy: Trading strategy to test
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            Dict with backtest results
        """
        # Reset state
        self.current_capital = self.initial_capital
        self.cash = self.initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
        self.daily_returns = []
        self.equity_curve = []
        
        # Get all trading days
        all_dates = set()
        for symbol, data in self.data.items():
            symbol_dates = data.index[(data.index >= start_date) & (data.index <= end_date)]
            all_dates.update(symbol_dates)
            
        trading_days = sorted(all_dates)
        
        if not trading_days:
            return {"error": "No trading days found in specified date range"}
            
        # Run backtest day by day
        for i, current_date in enumerate(trading_days):
            # Get current data for all symbols
            current_data = {}
            for symbol, data in self.data.items():
                if current_date in data.index:
                    current_data[symbol] = data.loc[:current_date]
                    
            if not current_data:
                continue
                
            # Generate signals - create proper data structure for strategy
            try:
                # Combine data for strategy - create a DataFrame with Close prices for each symbol
                combined_data = pd.DataFrame()
                for symbol, data in current_data.items():
                    if 'Close' in data.columns:
                        combined_data[symbol] = data['Close']
                
                if not combined_data.empty:
                    signals = strategy.generate_signals(combined_data, current_date)
                else:
                    signals = {}
            except Exception as e:
                print(f"Error generating signals: {e}")
                signals = {}
            
            # Execute trades based on signals
            for symbol, signal in signals.items():
                if symbol in current_data and signal in ['buy', 'sell']:
                    # Fix Series ambiguity in price extraction
                    symbol_data = current_data[symbol]
                    if current_date in symbol_data.index:
                        price_data = symbol_data.loc[current_date, 'Close']
                        if isinstance(price_data, pd.Series):
                            current_price = price_data.iloc[0] if len(price_data) > 0 else price_data
                        else:
                            current_price = price_data
                    else:
                        continue  # Skip if no data for this date
                    
                    portfolio_value = self.calculate_portfolio_value(current_date)
                    
                    if signal == 'buy':
                        quantity = strategy.calculate_position_size(
                            symbol, signal, portfolio_value, self.positions
                        )
                        if quantity > 0:
                            self.execute_trade(symbol, OrderSide.BUY, quantity, current_price, current_date)
                            
                    elif signal == 'sell':
                        if symbol in self.positions and self.positions[symbol].quantity > 0:
                            quantity = strategy.calculate_position_size(
                                symbol, signal, portfolio_value, self.positions
                            )
                            if quantity > 0:
                                self.execute_trade(symbol, OrderSide.SELL, quantity, current_price, current_date)
                                
            # Record portfolio value
            portfolio_value = self.calculate_portfolio_value(current_date)
            self.portfolio_values.append((current_date, portfolio_value))
            self.equity_curve.append(portfolio_value)
            
            # Calculate daily returns
            if i > 0:
                daily_return = (portfolio_value - self.portfolio_values[i-1][1]) / self.portfolio_values[i-1][1]
                self.daily_returns.append(daily_return)
                
        # Calculate performance metrics
        return self.calculate_performance_metrics()
        
    def calculate_performance_metrics(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        if not self.portfolio_values:
            return {"error": "No portfolio data available"}
            
        final_value = self.portfolio_values[-1][1]
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # Calculate daily returns
        daily_returns = np.array(self.daily_returns)
        
        # Basic metrics
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.portfolio_value_after > t.portfolio_value_before])
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Risk metrics
        if len(daily_returns) > 0:
            sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252) if np.std(daily_returns) > 0 else 0
            
            # Sortino ratio (downside deviation)
            downside_returns = daily_returns[daily_returns < 0]
            downside_deviation = np.std(downside_returns) if len(downside_returns) > 0 else 0
            sortino_ratio = np.mean(daily_returns) / downside_deviation * np.sqrt(252) if downside_deviation > 0 else 0
            
            # Maximum drawdown
            equity_curve = np.array(self.equity_curve)
            running_max = np.maximum.accumulate(equity_curve)
            drawdown = (equity_curve - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
        else:
            sharpe_ratio = 0
            sortino_ratio = 0
            max_drawdown = 0
            
        # Transaction costs
        total_transaction_costs = sum(trade.transaction_cost for trade in self.trades)
        
        return {
            "initial_capital": self.initial_capital,
            "final_value": final_value,
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": win_rate,
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown * 100,
            "total_transaction_costs": total_transaction_costs,
            "transaction_cost_pct": (total_transaction_costs / self.initial_capital) * 100,
            "trades": self.trades,
            "portfolio_values": self.portfolio_values,
            "equity_curve": self.equity_curve
        }
        
    def plot_results(self, results: Dict) -> go.Figure:
        """Create comprehensive backtest visualization"""
        if "portfolio_values" not in results:
            return go.Figure()
            
        # Create equity curve
        dates, values = zip(*results["portfolio_values"])
        
        fig = go.Figure()
        
        # Add equity curve
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines',
            name='Portfolio Value',
            line=dict(color='blue', width=2)
        ))
        
        # Add initial capital line
        fig.add_hline(
            y=self.initial_capital,
            line_dash="dash",
            line_color="red",
            annotation_text="Initial Capital"
        )
        
        # Add trade markers
        buy_trades = [t for t in results["trades"] if t.side == OrderSide.BUY]
        sell_trades = [t for t in results["trades"] if t.side == OrderSide.SELL]
        
        if buy_trades:
            buy_dates = [t.timestamp for t in buy_trades]
            buy_values = [t.portfolio_value_after for t in buy_trades]
            fig.add_trace(go.Scatter(
                x=buy_dates,
                y=buy_values,
                mode='markers',
                name='Buy',
                marker=dict(color='green', size=8, symbol='triangle-up')
            ))
            
        if sell_trades:
            sell_dates = [t.timestamp for t in sell_trades]
            sell_values = [t.portfolio_value_after for t in sell_trades]
            fig.add_trace(go.Scatter(
                x=sell_dates,
                y=sell_values,
                mode='markers',
                name='Sell',
                marker=dict(color='red', size=8, symbol='triangle-down')
            ))
            
        fig.update_layout(
            title="Backtest Results - Portfolio Value Over Time",
            xaxis_title="Date",
            yaxis_title="Portfolio Value (₹)",
            height=600,
            showlegend=True
        )
        
        return fig


# Example Strategy Implementation
class MovingAverageStrategy(TradingStrategy):
    """Simple moving average crossover strategy"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50, position_size_pct: float = 0.1):
        self.short_window = short_window
        self.long_window = long_window
        self.position_size_pct = position_size_pct
        
    def generate_signals(self, data: pd.DataFrame, timestamp: datetime) -> Dict[str, str]:
        """Generate signals based on moving average crossover"""
        signals = {}
        
        # Handle multi-symbol data (each column is a symbol's Close price)
        for symbol in data.columns:
            symbol_data = data[symbol].dropna()  # Remove NaN values
            
            if len(symbol_data) < self.long_window:
                signals[symbol] = 'hold'
                continue
                
            # Calculate moving averages
            short_ma = symbol_data.iloc[-self.short_window:].mean()
            long_ma = symbol_data.iloc[-self.long_window:].mean()
            
            # Generate signals with sensitivity - ensure scalar comparison
            if pd.notna(short_ma) and pd.notna(long_ma):
                # Convert to float to ensure scalar comparison
                short_ma_val = float(short_ma)
                long_ma_val = float(long_ma)
                
                # Add a small threshold to avoid noise
                threshold = 0.001  # 0.1% threshold
                if short_ma_val > long_ma_val * (1 + threshold):
                    signals[symbol] = 'buy'
                elif short_ma_val < long_ma_val * (1 - threshold):
                    signals[symbol] = 'sell'
                else:
                    signals[symbol] = 'hold'
            else:
                signals[symbol] = 'hold'
                        
        return signals
        
    def calculate_position_size(self, symbol: str, signal: str, portfolio_value: float, 
                              current_positions: Dict[str, Position]) -> int:
        """Calculate position size based on percentage of portfolio"""
        if signal == 'buy':
            position_value = portfolio_value * self.position_size_pct
            # Return a reasonable position size (simplified)
            return max(1, int(position_value / 1000))  # At least 1 share
        elif signal == 'sell':
            if symbol in current_positions and current_positions[symbol].quantity > 0:
                return current_positions[symbol].quantity  # Sell all shares
        return 0


# Example usage
if __name__ == "__main__":
    # Create backtest engine
    engine = BacktestEngine(initial_capital=100000)
    
    # Add data (would fetch from Yahoo Finance in real usage)
    # engine.add_data("RELIANCE.NS", historical_data)
    
    # Create strategy
    strategy = MovingAverageStrategy(short_window=20, long_window=50)
    
    # Run backtest
    # results = engine.run_backtest(strategy, start_date, end_date)
    
    print("Backtesting engine initialized successfully!")
