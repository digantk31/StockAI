"""
Trading Page - Real-time Data and Backtesting
Advanced trading features with live data and strategy backtesting
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from src.backtesting_engine import BacktestEngine, MovingAverageStrategy, TransactionCost
from config.config import MARKET_GROUPS

def show_trading_page():
    """Main trading page with backtesting and performance analytics"""
    st.title("📊 Advanced Trading Center")
    st.markdown("Professional backtesting with transaction costs and comprehensive performance analytics")
    
    # Page tabs
    tab1, tab2 = st.tabs(["📈 Strategy Backtesting", "📋 Performance Analytics"])
    
    with tab1:
        show_backtesting_interface()
    
    with tab2:
        show_performance_analytics()


def show_backtesting_interface():
    """Strategy backtesting interface"""
    st.header("📈 Strategy Backtesting")
    st.markdown("Test trading strategies with realistic transaction costs")
    
    # Strategy selection
    st.subheader("Strategy Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        strategy_type = st.selectbox(
            "Select Strategy",
            ["Moving Average Crossover", "RSI Mean Reversion", "MACD Strategy"],
            index=0
        )
        
        if strategy_type == "Moving Average Crossover":
            short_window = st.slider("Short MA Period", 5, 50, 20)
            long_window = st.slider("Long MA Period", 20, 200, 50)
            
        elif strategy_type == "RSI Mean Reversion":
            rsi_period = st.slider("RSI Period", 5, 30, 14)
            oversold = st.slider("Oversold Level", 10, 30, 20)
            overbought = st.slider("Overbought Level", 70, 90, 80)
            
        else:  # MACD
            fast_period = st.slider("MACD Fast", 8, 20, 12)
            slow_period = st.slider("MACD Slow", 20, 40, 26)
            signal_period = st.slider("Signal Period", 5, 15, 9)
    
    with col2:
        # Backtesting parameters
        initial_capital = st.number_input(
            "Initial Capital (₹)",
            min_value=10000,
            max_value=10000000,
            value=100000,
            step=10000
        )
        
        position_size_pct = st.slider(
            "Position Size (%)",
            min_value=1,
            max_value=50,
            value=10
        ) / 100
        
        # Transaction costs
        st.subheader("Transaction Costs")
        brokerage_fee = st.slider("Brokerage Fee (%)", 0.0, 1.0, 0.01) / 100
        stt_tax = st.slider("STT Tax (%)", 0.0, 1.0, 0.06) / 100
        slippage = st.slider("Slippage (%)", 0.0, 1.0, 0.05) / 100
        
    # Stock selection for backtesting
    st.subheader("Stock Selection")
    selected_market_bt = st.selectbox("Select Market for Backtesting", options=list(MARKET_GROUPS.keys()), index=0)
    
    if selected_market_bt == "All":
        available_stocks_bt = MARKET_GROUPS["All"][:10]  # Limit for backtesting
    else:
        available_stocks_bt = MARKET_GROUPS[selected_market_bt]
    
    selected_stocks_bt = st.multiselect(
        "Select Stocks for Backtesting",
        options=available_stocks_bt,
        default=available_stocks_bt[:3]
    )
    
    # Add a note about selection limit
    if len(selected_stocks_bt) > 5:
        st.warning("For better performance, please select no more than 5 stocks for backtesting.")
        selected_stocks_bt = selected_stocks_bt[:5]
    
    # Date range
    start_date = st.date_input("Start Date", datetime(2022, 1, 1))
    end_date = st.date_input("End Date", datetime.now() - timedelta(days=1))
    
    # Run backtest button
    if st.button("🚀 Run Backtest", type="primary") and selected_stocks_bt:
        with st.spinner("Running backtest with transaction costs..."):
            try:
                # Initialize backtest engine
                transaction_cost = TransactionCost(
                    brokerage_fee=brokerage_fee,
                    stt_tax=stt_tax,
                    slippage=slippage
                )
                
                engine = BacktestEngine(
                    initial_capital=initial_capital,
                    transaction_cost=transaction_cost
                )
                
                # Fetch historical data
                for symbol in selected_stocks_bt:
                    data = yf.download(symbol, start=start_date, end=end_date)
                    if not data.empty:
                        engine.add_data(symbol, data)
                
                # Create strategy
                if strategy_type == "Moving Average Crossover":
                    strategy = MovingAverageStrategy(
                        short_window=short_window,
                        long_window=long_window,
                        position_size_pct=position_size_pct
                    )
                else:
                    # Placeholder for other strategies
                    strategy = MovingAverageStrategy(
                        short_window=short_window,
                        long_window=long_window,
                        position_size_pct=position_size_pct
                    )
                
                # Convert date objects to datetime for backtesting
                start_datetime = datetime.combine(start_date, datetime.min.time())
                end_datetime = datetime.combine(end_date, datetime.max.time())
                
                # Run backtest
                results = engine.run_backtest(strategy, start_datetime, end_datetime)
                
                # Display results
                if "error" not in results:
                    st.session_state.backtest_results = results
                    st.success("Backtest completed successfully!")
                else:
                    st.error(f"Backtest failed: {results['error']}")
                    
            except Exception as e:
                st.error(f"Error running backtest: {str(e)}")
    
    # Display backtest results
    if 'backtest_results' in st.session_state:
        results = st.session_state.backtest_results
        display_backtest_results(results)

def display_backtest_results(results):
    """Display comprehensive backtest results"""
    st.subheader("📊 Backtest Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Return",
            f"{results['total_return_pct']:.2f}%",
            f"₹{results['final_value'] - results['initial_capital']:,.0f}"
        )
    
    with col2:
        st.metric("Sharpe Ratio", f"{results['sharpe_ratio']:.3f}")
    
    with col3:
        st.metric("Max Drawdown", f"{results['max_drawdown_pct']:.2f}%")
    
    with col4:
        st.metric("Win Rate", f"{results['win_rate']*100:.1f}%")
    
    # Detailed metrics
    st.subheader("📈 Performance Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Trading Statistics**")
        st.write(f"- Total Trades: {results['total_trades']}")
        st.write(f"- Winning Trades: {results['winning_trades']}")
        st.write(f"- Win Rate: {results['win_rate']*100:.1f}%")
        st.write(f"- Sortino Ratio: {results['sortino_ratio']:.3f}")
        
    with col2:
        st.write("**Financial Metrics**")
        st.write(f"- Initial Capital: ₹{results['initial_capital']:,.0f}")
        st.write(f"- Final Value: ₹{results['final_value']:,.0f}")
        st.write(f"- Total Return: {results['total_return_pct']:.2f}%")
        st.write(f"- Transaction Costs: ₹{results['total_transaction_costs']:,.0f}")
        st.write(f"- Cost Impact: {results['transaction_cost_pct']:.2f}%")
    
    # Equity curve
    st.subheader("📊 Equity Curve")
    
    # Create figure
    engine = BacktestEngine()  # Create dummy engine for plotting
    fig = engine.plot_results(results)
    st.plotly_chart(fig, width='stretch')
    
    # Trade log
    if results['trades']:
        st.subheader("📋 Trade Log")
        
        trades_df = pd.DataFrame([
            {
                'Date': trade.timestamp.strftime('%Y-%m-%d %H:%M'),
                'Symbol': trade.symbol,
                'Side': trade.side.value,
                'Quantity': trade.quantity,
                'Price': f"₹{trade.price:.2f}",
                'Value': f"₹{trade.trade_value:,.0f}",
                'Cost': f"₹{trade.transaction_cost:.2f}",
                'Portfolio Value': f"₹{trade.portfolio_value_after:,.0f}"
            }
            for trade in results['trades'][-20:]  # Show last 20 trades
        ])
        
        st.dataframe(trades_df, width='stretch')

def show_performance_analytics():
    """Performance analytics and comparison"""
    st.header("📋 Performance Analytics")
    st.markdown("Detailed performance analysis and strategy comparison")
    
    if 'backtest_results' not in st.session_state:
        st.info("Run a backtest first to see performance analytics")
        return
    
    results = st.session_state.backtest_results
    
    # Performance charts
    st.subheader("📊 Performance Analysis")
    
    # Monthly returns heatmap
    if results['portfolio_values'] and len(results['portfolio_values']) > 1:
        portfolio_df = pd.DataFrame(results['portfolio_values'], columns=['Date', 'Value'])
        portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])
        portfolio_df['Returns'] = portfolio_df['Value'].pct_change()
        portfolio_df['Year'] = portfolio_df['Date'].dt.year
        portfolio_df['Month'] = portfolio_df['Date'].dt.month
        
        # Create monthly returns matrix
        monthly_returns = portfolio_df.groupby(['Year', 'Month'])['Returns'].mean().unstack()
        
        if not monthly_returns.empty:
            st.write("**Monthly Returns Heatmap**")
            fig = px.imshow(
                monthly_returns.T * 100,
                labels=dict(x="Year", y="Month", color="Return (%)"),
                color_continuous_scale="RdYlGn",
                aspect="auto"
            )
            st.plotly_chart(fig, width='stretch')
    else:
        st.info("No portfolio data available for monthly returns analysis")
    
    # Risk metrics
    st.subheader("⚠️ Risk Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Risk Metrics**")
        st.write(f"- Sharpe Ratio: {results['sharpe_ratio']:.3f}")
        st.write(f"- Sortino Ratio: {results['sortino_ratio']:.3f}")
        st.write(f"- Max Drawdown: {results['max_drawdown_pct']:.2f}%")
        
        # Calculate additional metrics
        if 'daily_returns' in results and results['daily_returns']:
            daily_returns = np.array(results['daily_returns'])
            var_95 = np.percentile(daily_returns, 5)
            var_99 = np.percentile(daily_returns, 1)
            st.write(f"- VaR (95%): {var_95*100:.2f}%")
            st.write(f"- VaR (99%): {var_99*100:.2f}%")
        else:
            st.write("- VaR (95%): N/A (insufficient data)")
            st.write("- VaR (99%): N/A (insufficient data)")
    
    with col2:
        st.write("**Transaction Cost Analysis**")
        st.write(f"- Total Costs: ₹{results['total_transaction_costs']:,.0f}")
        if results['total_trades'] > 0:
            st.write(f"- Cost per Trade: ₹{results['total_transaction_costs']/results['total_trades']:,.0f}")
        else:
            st.write("- Cost per Trade: N/A (no trades)")
        st.write(f"- Cost Impact: {results['transaction_cost_pct']:.2f}%")
        if results['transaction_cost_pct'] > 0:
            st.write(f"- Cost Efficiency: {results['total_return_pct']/results['transaction_cost_pct']:.1f}x")
        else:
            st.write("- Cost Efficiency: N/A (no transaction costs)")
    
    # Strategy comparison
    st.subheader("🔄 Strategy Comparison")
    st.info("Compare multiple strategies side by side (feature coming soon)")
    
    # Export functionality
    st.subheader("📤 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to CSV"):
            # Create export data
            export_data = {
                'Metric': ['Total Return', 'Sharpe Ratio', 'Max Drawdown', 'Win Rate', 'Total Trades'],
                'Value': [
                    f"{results['total_return_pct']:.2f}%",
                    f"{results['sharpe_ratio']:.3f}",
                    f"{results['max_drawdown_pct']:.2f}%",
                    f"{results['win_rate']*100:.1f}%",
                    results['total_trades']
                ]
            }
            export_df = pd.DataFrame(export_data)
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Generate Report"):
            st.success("Report generation feature coming soon!")

if __name__ == "__main__":
    show_trading_page()
