# StockAI - AI-Powered Stock Market Intelligence

![StockAI Banner](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4EBx9mg3Tzc8Xg4ayJi2wtrXGjJDNHBc8KQ&s)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/digantk31/StockAI)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stockai-app.streamlit.app/)

## 📌 Overview
StockAI is a comprehensive **AI/ML-powered Stock Intelligence Platform** built as a final year BTech CSE project. It combines statistical modeling, deep learning, ensemble methods, and NLP to analyze stocks, forecast prices, and optimize portfolios.

The application has three main modules:
1.  **Stock Forecast** — Predict future prices using time-series analysis (SARIMAX)
2.  **Portfolio Analysis** — Find the best stock combinations using optimization & risk analysis
3.  **Advanced AI** — Multiple AI models for price prediction, trend signals, and news sentiment

## 🚀 Key Features

### 1. Stock Price Forecasting
- **Time Series Breakdown** — Visual separation of trend, seasonality, and noise
- **Customizable Model** — Adjust forecasting parameters (p, d, q) and seasonal settings (P, D, Q, S)
- **Stability Check** — Augmented Dickey-Fuller test to verify data is forecastable
- **Real-World Accuracy Check** — Backtesting: hides last 30 days to honestly test predictions
- **Interactive Charts** — Plotly-powered Actual vs Model Fit vs Forecast visualization

### 2. Portfolio Analysis
- **Stock Connections** — Interactive correlation heatmap showing how stocks move together
- **Performance Comparison** — Cumulative returns vs NIFTY 50 benchmark
- **Risk vs Return Map** — Efficient Frontier with 1000+ simulated portfolios
- **Best Portfolios** — Finds the **Best Returns** and **Safest** portfolio combinations
- **Allocation Charts** — Pie charts showing how to split your investment
- **Safety Analysis** — Market Sensitivity (Beta), Biggest Loss from Peak, and crash simulation

### 3. Advanced AI (6 AI/ML Algorithms)
- **FinBERT Sentiment** — Reads news headlines using a financial AI language model (HuggingFace Transformer). Falls back to TextBlob if unavailable.
- **AI Trade Signal** — Random Forest Classifier on price patterns (RSI, SMA) predicts Buy/Sell with confidence and **feature importance chart**
- **MLP Neural Network** — Multi-Layer Perceptron for 30-day price forecast
- **LSTM Deep Learning** — Long Short-Term Memory recurrent network (TensorFlow/Keras) for sequential price prediction. Falls back to GradientBoosting with temporal features if TensorFlow unavailable.
- **Model Comparison** — Side-by-side MLP vs LSTM with combined forecast chart and metrics (R², RMSE, MAE)
- **Auto-fallback** — Gracefully switches to alternative models based on available libraries

## 🛠️ Technologies Used
| Category | Technology |
|----------|-----------|
| Frontend | Streamlit (dark theme) |
| Data Source | Yahoo Finance (`yfinance`) |
| Statistical Modeling | statsmodels (SARIMAX) |
| Machine Learning | Scikit-Learn (MLP, Random Forest, GradientBoosting) |
| Deep Learning | TensorFlow/Keras (LSTM) |
| NLP | FinBERT (HuggingFace Transformers) + TextBlob (fallback) |
| Portfolio Optimization | SciPy (`scipy.optimize`) |
| Visualization | Plotly (interactive charts) |
| Data Processing | Pandas, NumPy |

## 📁 Project Structure
```
StockAI/
├── app.py                          # Entry point & navigation
├── .streamlit/
│   └── config.toml                 # Dark theme configuration
├── views/                          # Streamlit page modules
│   ├── __init__.py
│   ├── forecast_page.py            # SARIMAX forecasting page
│   ├── portfolio_page.py           # Portfolio analysis page
│   └── ai_page.py                  # Advanced AI insights page
├── src/                            # Core analytics & AI engine
│   ├── __init__.py
│   ├── ai_features.py              # MLP, LSTM, GradientBoosting, Random Forest, FinBERT
│   ├── data_fetcher.py             # Yahoo Finance data fetching & cleaning
│   ├── returns_analysis.py         # Daily, monthly, annual returns & CAGR
│   ├── correlation_analysis.py     # Correlation matrix & diversification metrics
│   ├── portfolio_optimizer.py      # Mean-variance optimization & efficient frontier
│   ├── risk_metrics.py             # Sharpe, Sortino, Beta, Alpha, VaR
│   └── stress_testing.py           # Stress scenarios, drawdown & VaR/CVaR
├── config/
│   ├── __init__.py
│   └── config.py                   # Tickers, date ranges, risk-free rate, scenarios
├── .gitignore
├── requirements.txt
└── README.md
```

## 📋 Installation

1. Clone the repository:
```bash
git clone https://github.com/digantk31/StockAI.git
cd StockAI
```

2. Create and activate a virtual environment (**Python 3.12 recommended**):
```bash
py -3.12 -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install tensorflow transformers torch
```

> **Note**: `tensorflow`, `transformers`, and `torch` are optional. The app works without them using built-in fallback models (GradientBoosting for LSTM, TextBlob for FinBERT).

4. Run the application:
```bash
streamlit run app.py
```

## 🖥️ How to Use
1.  **Navigate** using the sidebar to choose between pages
2.  **Stock Forecast** — Enter a stock ticker (e.g., AAPL), adjust settings, click "Run Forecast". Use backtesting to check real-world accuracy.
3.  **Portfolio Analysis** — Enter multiple tickers (e.g., `RELIANCE.NS, TCS.NS, HDFCBANK.NS`) to see which combination gives best returns with least risk.
4.  **Advanced AI** — Enter a ticker to get AI-powered sentiment, trend signals, and price predictions from multiple models.

## 📸 What You'll See
- **Risk vs Return Map** — Scatter plot showing best portfolio combinations
- **AI Price Forecast** — 30-day future price prediction from two AI models
- **News Sentiment** — Table of recent news with positive/negative scores
- **Model Comparison** — Which AI model predicts better for your stock
- **Feature Importance** — What factors the AI relies on most

## 📸 Sample Outputs

### Stock Price Forecast
![Stock Forecast — Actual vs Predicted vs Future](assets/forecast.png)

### Portfolio Optimization
![Best Portfolio Combinations — Max Returns vs Safest](assets/portfolio_optimization.png)

### Risk vs Return Map (Efficient Frontier)
![Efficient Frontier — 1000+ Simulated Portfolios](assets/efficient_frontier.png)

### AI Model Comparison (MLP vs LSTM)
![Model Comparison — 30-Day Forecast from Two AI Models](assets/model_comparison.png)

### AI Insights — Sentiment & Feature Importance
![AI Insights — News Sentiment and Feature Importance](assets/ai_insights.png)

## ⚠️ Disclaimer
This application is built for **educational and academic purposes only**. The predictions, signals, and analysis should **not** be used as financial advice or for real trading decisions.

## 🔗 Links
- **GitHub Repository**: [GitHub](https://github.com/digantk31/StockAI)

## 👤 Author
- **Digant Kathiriya**
