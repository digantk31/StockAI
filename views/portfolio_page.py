
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import pandas as pd
# Local imports
from src import DataFetcher, ReturnsAnalysis, CorrelationAnalysis, PortfolioOptimizer
<<<<<<< HEAD
from config.config import MARKET_GROUPS, BENCHMARK_TICKERS
=======
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0

def show_portfolio_page():
    st.title("Stock Portfolio Analysis")
    st.markdown("""
    This tool helps you find the **best combination of stocks** to maximize returns while keeping risk low.
    It uses proven financial math (Modern Portfolio Theory) to optimize your portfolio.
    """)
    
    # Portfolio Input
    st.sidebar.header("Portfolio Settings")
    
<<<<<<< HEAD
    # Market Selection
    selected_market = st.sidebar.selectbox("Select Market", options=list(MARKET_GROUPS.keys()), index=0)
    
    # Auto-populate tickers based on market selection
    if selected_market == "All":
        default_tickers = ", ".join(MARKET_GROUPS["All"][:15])  # Show first 15 to avoid clutter
    else:
        default_tickers = ", ".join(MARKET_GROUPS[selected_market])
=======
    # Predefined list of NIFTY 50 stocks (simplified)
    default_tickers = "RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS, ITC.NS"
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
    
    tickers_input = st.sidebar.text_area("Enter Stock Tickers (comma separated)", 
                                         value=default_tickers, height=100)
    
    # Clean and parse tickers
    tickers = [t.strip().upper() for t in tickers_input.split(',')]
    # Remove empty strings if user left a trailing comma
    tickers = [t for t in tickers if t]
    
    start_date = st.sidebar.date_input("Start Date", date(2021, 1, 1))
    end_date = st.sidebar.date_input("End Date", date(2024, 1, 1))
    
    run_analysis_btn = st.sidebar.button("Run Portfolio Analysis")

    if run_analysis_btn:
        if len(tickers) < 2:
            st.warning("Please enter at least 2 stocks for portfolio analysis.")
            return

        with st.spinner("Fetching data and running optimization..."):
            try:
                # Convert date objects to string YYYY-MM-DD
                start_str = start_date.strftime('%Y-%m-%d')
                end_str = end_date.strftime('%Y-%m-%d')
                
                # 1. Fetch Data
<<<<<<< HEAD
                # Determine the appropriate benchmark based on selected market
                benchmark_ticker = BENCHMARK_TICKERS.get(selected_market, "^NSEI")
                fetcher = DataFetcher(tickers=tickers, start_date=start_str, end_date=end_str)
                stock_data = fetcher.fetch_stock_data(save_to_csv=False)
                
                # Override the benchmark in fetcher
                fetcher.benchmark = benchmark_ticker
                
=======
                fetcher = DataFetcher(tickers=tickers, start_date=start_str, end_date=end_str)
                stock_data = fetcher.fetch_stock_data(save_to_csv=False)
                
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
                # --- VALIDATION LOGIC ---
                fetched_tickers = stock_data.columns.tolist()
                invalid_tickers = [t for t in tickers if t not in fetched_tickers]
                
                if invalid_tickers:
                    st.error(f"❌ **Invalid Tickers Found**: The following stocks could not be fetched: `{', '.join(invalid_tickers)}`.")
                
                # Proceed only with valid tickers
                if stock_data.empty:
                    st.error("No valid data fetched. Please check all your tickers.")
                    return
                
                tickers = fetched_tickers 
                
                if len(tickers) < 2:
                    st.warning("⚠️ Fewer than 2 valid stocks remain. Need at least 2 for portfolio analysis.")
                    return
                elif invalid_tickers:
                     st.success(f"Running analysis on the remaining **{len(tickers)}** valid stocks.")
                else:
                     st.success(f"Data successfully fetched for all **{len(tickers)}** stocks.")
                
                # 2. Calculate Returns
                returns_analyzer = ReturnsAnalysis(stock_data)
                daily_returns = returns_analyzer.calculate_daily_returns()
                
                st.subheader("Returns Analysis")
                st.dataframe(daily_returns.tail())
                
                # 3. Correlation Analysis
                corr_analyzer = CorrelationAnalysis(daily_returns)
                correlation_matrix = corr_analyzer.calculate_correlation_matrix()
                
                st.subheader("How Are These Stocks Connected? (Correlation)")
                fig_corr = px.imshow(correlation_matrix, text_auto=True, aspect="auto",
                                     title="Stock Correlation Heatmap",
                                     color_continuous_scale='RdBu_r')
                st.plotly_chart(fig_corr)

                # --- 4. Cumulative Returns vs Benchmark ---
<<<<<<< HEAD
                benchmark_name = selected_market if selected_market != "All" else "S&P 500"
                st.subheader(f"Performance Comparison (Growth of 1) vs {benchmark_name}")
                
                benchmark_data = None
                with st.spinner(f"Fetching Benchmark ({benchmark_ticker}) data..."):
=======
                st.subheader("Performance Comparison (Growth of ₹1)")
                
                benchmark_data = None
                with st.spinner("Fetching Benchmark (NIFTY 50) data..."):
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
                    try:
                        benchmark_data = fetcher.fetch_benchmark_data(save_to_csv=False)
                        common_index = stock_data.index.intersection(benchmark_data.index)
                        aligned_stocks = stock_data.loc[common_index]
                        aligned_bench = benchmark_data.loc[common_index]
                        
                        stock_returns = aligned_stocks.pct_change()
                        bench_returns = aligned_bench.pct_change()
                        
                        stock_cum_ret = (1 + stock_returns.fillna(0)).cumprod()
                        bench_cum_ret = (1 + bench_returns.fillna(0)).cumprod()
                        
                        fig_cum = go.Figure()
                        fig_cum.add_trace(go.Scatter(x=bench_cum_ret.index, y=bench_cum_ret, mode='lines', 
<<<<<<< HEAD
                                                     name=f'{benchmark_name} (Benchmark)', line=dict(color='black', width=3, dash='dash')))
=======
                                                     name='NIFTY 50 (Benchmark)', line=dict(color='black', width=3, dash='dash')))
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
                        
                        for col in stock_cum_ret.columns:
                            fig_cum.add_trace(go.Scatter(x=stock_cum_ret.index, y=stock_cum_ret[col], mode='lines', name=col, opacity=0.7))
                            
                        fig_cum.update_layout(title="Cumulative Returns Comparison", xaxis_title="Date", yaxis_title="Growth of $1", height=500)
                        st.plotly_chart(fig_cum)
                        
                    except Exception as e:
                        st.warning(f"Could not load benchmark comparison: {e}")
                
                # 5. Optimization
                st.subheader("Best Portfolio Combinations")
                optimizer = PortfolioOptimizer(daily_returns)
                max_sharpe = optimizer.optimize_sharpe_ratio()
                min_vol = optimizer.optimize_min_volatility()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success("🏆 Best Returns Portfolio")
                    st.metric("Expected Yearly Return", f"{max_sharpe['return']*100:.2f}%")
                    st.metric("Risk Level (Volatility)", f"{max_sharpe['volatility']*100:.2f}%", help="How much the price swings — lower is safer")
                    st.metric("Risk-Adjusted Score (Sharpe)", f"{max_sharpe['sharpe_ratio']:.4f}", help="Higher = better returns for the risk taken")
                    fig_pie1 = px.pie(values=list(max_sharpe['weights'].values()), names=list(max_sharpe['weights'].keys()), title="Best Returns — How to Split Your Money")
                    st.plotly_chart(fig_pie1)

                with col2:
                    st.info("🛡️ Safest Portfolio")
                    st.metric("Expected Yearly Return", f"{min_vol['return']*100:.2f}%")
                    st.metric("Risk Level (Volatility)", f"{min_vol['volatility']*100:.2f}%", help="Lowest possible risk")
                    st.metric("Risk-Adjusted Score (Sharpe)", f"{min_vol['sharpe_ratio']:.4f}")
                    fig_pie2 = px.pie(values=list(min_vol['weights'].values()), names=list(min_vol['weights'].keys()), title="Safest — How to Split Your Money")
                    st.plotly_chart(fig_pie2)
                
                # Efficient Frontier
                st.subheader("Risk vs Return Map (Efficient Frontier)")
                st.markdown("*Each dot is a possible portfolio. The curve shows the best combinations.*")
                frontier = optimizer.generate_efficient_frontier(50)
                random_portfolios = optimizer.generate_random_portfolios(1000)
                
                fig_ef = go.Figure()
                fig_ef.add_trace(go.Scatter(x=random_portfolios['Volatility'], y=random_portfolios['Return'],
                                            mode='markers', name='Random Portfolios', marker=dict(color=random_portfolios['Sharpe Ratio'], colorscale='Viridis', size=5)))
                
                fig_ef.add_trace(go.Scatter(x=frontier['Volatility'], y=frontier['Return'], mode='lines', name='Efficient Frontier', line=dict(color='black', width=2, dash='dash')))
                
                fig_ef.add_trace(go.Scatter(x=[max_sharpe['volatility']], y=[max_sharpe['return']], mode='markers', name='Max Sharpe', marker=dict(color='red', size=15, symbol='star')))
                fig_ef.add_trace(go.Scatter(x=[min_vol['volatility']], y=[min_vol['return']], mode='markers', name='Min Volatility', marker=dict(color='blue', size=15, symbol='triangle-up')))
                
                fig_ef.update_layout(title="Risk vs Return — Finding the Sweet Spot", xaxis_title="Risk (Volatility)", yaxis_title="Expected Return", height=600)
                st.plotly_chart(fig_ef)

                # --- 6. Advanced Risk & Stress Testing (New Requirement) ---
                st.markdown("---")
                st.header("How Safe Is This Portfolio?")
                st.markdown("*Testing how the **Best Returns Portfolio** would perform during market crashes.*")
                
                try:
                    # We need the max sharpe weights to construct the portfolio equity curve
                    ms_weights = max_sharpe['weights']
                    
                    # Calculate Portfolio Daily Returns (Weighted sum)
                    # Use aligned data for safety
                    if benchmark_data is not None:
                         # Re-calculate to be sure
                         aligned_stocks_rets = stock_data.loc[common_index].pct_change().fillna(0)
                         bench_rets = benchmark_data.loc[common_index].pct_change().fillna(0)
                    else:
                         # Fallback if benchmark failed
                         aligned_stocks_rets = daily_returns
                         bench_rets = None
                    
                    portfolio_daily_ret = aligned_stocks_rets.mul(pd.Series(ms_weights)).sum(axis=1)
                    
                    # 1. Beta Calculation
                    if bench_rets is not None:
                        covariance = portfolio_daily_ret.cov(bench_rets)
                        variance = bench_rets.var()
                        if variance > 0:
                            beta = covariance / variance
                            st.metric("Market Sensitivity (Beta)", f"{beta:.2f}", 
                                      help="Above 1 = your portfolio moves MORE than the market. Below 1 = LESS than market.")
                        else:
                            beta = 1.0 # Default fallback
                            st.warning("Benchmark variance is 0, assuming Beta = 1.0")
                    else:
                        beta = 1.0
                        st.warning("Benchmark data missing, assuming Beta = 1.0 for stress test.")

                    # 2. Maximum Drawdown Analysis
                    cum_ret = (1 + portfolio_daily_ret).cumprod()
                    running_max = cum_ret.cummax()
                    drawdown = (cum_ret - running_max) / running_max
                    max_dd = drawdown.min()
                    
                    col_dd1, col_dd2 = st.columns(2)
                    with col_dd1:
                        st.metric("Biggest Loss from Peak", f"{max_dd*100:.2f}%", help="The worst drop from the highest point — shows worst-case historical scenario.")
                    
                    # Plot Drawdown
                    fig_dd = go.Figure()
                    fig_dd.add_trace(go.Scatter(x=drawdown.index, y=drawdown, 
                                                fill='tozeroy', line=dict(color='red'), name='Drawdown'))
                    fig_dd.update_layout(title="Portfolio Drawdown Over Time", yaxis_title="Drawdown %", height=300)
                    st.plotly_chart(fig_dd)
                    
                    # 3. Stress Testing (Scenario Analysis)
                    st.subheader("What If the Market Crashes?")
<<<<<<< HEAD
                    st.write(f"If {benchmark_name} drops by X%, here's how your portfolio would be affected:")
=======
                    st.write("If NIFTY 50 drops by X%, here's how your portfolio would be affected:")
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
                    
                    scenarios = [-10, -20, -30, -50] # Percent drops
                    stress_data = []
                    for drop in scenarios:
                        est_port_drop = drop * beta
                        stress_data.append({
                            "Market Scenario": f"Market Crash {drop}%",
                            "Estimated Portfolio Impact": f"{est_port_drop:.2f}%"
                        })
                    st.table(pd.DataFrame(stress_data))
                        
                except Exception as risk_error:
                    st.error(f"Error in Risk Analysis: {risk_error}")

            except Exception as e:
                import traceback
                st.error(f"An error occurred: {e}")
                st.text(traceback.format_exc())
