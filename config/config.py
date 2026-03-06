"""
Configuration settings for Stock Portfolio Analysis
"""
from datetime import datetime, timedelta

# Selected NIFTY 50 stocks across different sectors for diversification
STOCK_TICKERS = [
    "RELIANCE.NS",    # Energy
    "TCS.NS",         # IT Services
    "HDFCBANK.NS",    # Banking
    "INFY.NS",        # IT Services
    "HINDUNILVR.NS",  # FMCG
    "ICICIBANK.NS",   # Banking
    "BHARTIARTL.NS",  # Telecom
    "ITC.NS",         # FMCG
    "KOTAKBANK.NS",   # Banking
    "LT.NS",          # Infrastructure
]

# Stock sector mapping
STOCK_SECTORS = {
    "RELIANCE.NS": "Energy",
    "TCS.NS": "IT Services",
    "HDFCBANK.NS": "Banking",
    "INFY.NS": "IT Services",
    "HINDUNILVR.NS": "FMCG",
    "ICICIBANK.NS": "Banking",
    "BHARTIARTL.NS": "Telecom",
    "ITC.NS": "FMCG",
    "KOTAKBANK.NS": "Banking",
    "LT.NS": "Infrastructure",
}

# Date range for historical data (3 years)
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=3*365)

# Convert to string format for yfinance
START_DATE_STR = START_DATE.strftime("%Y-%m-%d")
END_DATE_STR = END_DATE.strftime("%Y-%m-%d")

# Benchmark index (NIFTY 50)
BENCHMARK_TICKER = "^NSEI"

# Risk-free rate (India 10-year government bond yield approximately)
RISK_FREE_RATE = 0.07  # 7% annual

# Trading days per year
TRADING_DAYS = 252

# Initial portfolio weights (equal weighted)
INITIAL_WEIGHTS = [1/len(STOCK_TICKERS)] * len(STOCK_TICKERS)

# Confidence levels for VaR
VAR_CONFIDENCE_LEVELS = [0.95, 0.99]

# Stress test scenarios (historical market crashes)
STRESS_SCENARIOS = {
    "COVID Crash 2020": -0.38,
    "2008 Financial Crisis": -0.52,
    "Dot-com Bubble 2000": -0.45,
    "Moderate Correction": -0.15,
    "Severe Recession": -0.30,
}

# Output directories
DATA_DIR = "data"
REPORTS_DIR = "reports"
