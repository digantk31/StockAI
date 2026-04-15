"""
Configuration settings for Stock Portfolio Analysis
"""
from datetime import datetime, timedelta

 
# Multi-market stock selections
INDIAN_STOCKS = [
 
# Selected NIFTY 50 stocks across different sectors for diversification
STOCK_TICKERS = [
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
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

 
US_STOCKS = [
    "AAPL",           # Technology
    "MSFT",           # Technology
    "GOOGL",          # Technology
    "AMZN",           # Consumer Discretionary
    "TSLA",           # Consumer Discretionary
    "JPM",            # Financial
    "JNJ",            # Healthcare
    "V",              # Financial
    "PG",             # Consumer Staples
    "NVDA",           # Technology
]

EUROPEAN_STOCKS = [
    "ASML.AS",        # Technology (Netherlands)
    "SAP.DE",         # Technology (Germany)
    "NESN.SW",        # Consumer Staples (Switzerland)
    "ROG.SW",         # Healthcare (Switzerland)
    "MC.PA",          # Consumer Goods (France)
    "SAN.PA",         # Healthcare (France)
    "DAI.DE",         # Automotive (Germany)
    "BMW.DE",         # Automotive (Germany)
    "HSBA.L",         # Financial (UK)
    "BP.L",           # Energy (UK)
]

# Default to Indian stocks (backward compatibility)
STOCK_TICKERS = INDIAN_STOCKS

# Stock sector mapping for all markets
STOCK_SECTORS = {
    # Indian Stocks
 
# Stock sector mapping
STOCK_SECTORS = {
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
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
 
    # US Stocks
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "AMZN": "Consumer Discretionary",
    "TSLA": "Consumer Discretionary",
    "JPM": "Financial",
    "JNJ": "Healthcare",
    "V": "Financial",
    "PG": "Consumer Staples",
    "NVDA": "Technology",
    # European Stocks
    "ASML.AS": "Technology",
    "SAP.DE": "Technology",
    "NESN.SW": "Consumer Staples",
    "ROG.SW": "Healthcare",
    "MC.PA": "Consumer Goods",
    "SAN.PA": "Healthcare",
    "DAI.DE": "Automotive",
    "BMW.DE": "Automotive",
    "HSBA.L": "Financial",
    "BP.L": "Energy",
}

# Market groupings
MARKET_GROUPS = {
    "Indian": INDIAN_STOCKS,
    "US": US_STOCKS,
    "European": EUROPEAN_STOCKS,
    "All": INDIAN_STOCKS + US_STOCKS + EUROPEAN_STOCKS
 
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
}

# Date range for historical data (3 years)
END_DATE = datetime.now()
START_DATE = END_DATE - timedelta(days=3*365)

# Convert to string format for yfinance
START_DATE_STR = START_DATE.strftime("%Y-%m-%d")
END_DATE_STR = END_DATE.strftime("%Y-%m-%d")

 
# Market-specific benchmark indices
BENCHMARK_TICKERS = {
    "Indian": "^NSEI",      # NIFTY 50
    "US": "^GSPC",          # S&P 500
    "European": "^STOXX50E", # STOXX Europe 50
}

# Default benchmark (backward compatibility)
 
# Benchmark index (NIFTY 50)
>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
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
