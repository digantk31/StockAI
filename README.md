# StockAI - Stock Market Forecasting App

![StockAI Banner](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4EBx9mg3Tzc8Xg4ayJi2wtrXGjJDNHBc8KQ&s)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/digantk31/StockAI)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stockai-app.streamlit.app/)

## 📌 Overview
StockAI is an interactive web application designed to forecast stock prices using historical data and SARIMAX modeling. The app provides:
- Real-time stock data visualization
- Time series decomposition (Trend, Seasonality, Residuals)
- Customizable forecasting parameters
- Interactive prediction visualizations

## 🚀 Features
- **Dynamic Data Visualization**: Interactive charts using Plotly
- **Time Series Decomposition**: Visual breakdown of trend, seasonality, and residuals
- **SARIMAX Modeling**: Customizable (p,d,q) parameters for accurate forecasting
- **Real-time Data**: Integration with Yahoo Finance API
- **User-friendly Interface**: Intuitive controls and parameter adjustments

## 🛠️ Technologies Used
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Forecasting**: statsmodels, SARIMAX
- **Data Source**: Yahoo Finance API (yfinance)

## 📋 Installation
1. Clone the repository:
```bash
git clone https://github.com/digantk31/StockAI.git
cd StockAI
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🖥️ Usage
Run the application:
```bash
streamlit run app.py
```

### App Workflow: 
1. Enter valid stock ticker symbol (e.g., AAPL)
2. Select date range using sidebar controls
3. Choose column for forecasting
4. Adjust SARIMAX parameters (p, d, q, seasonal period)
5. Set forecast duration (1-365 days)
6. Explore interactive visualizations and predictions

## 📈 Key Functionalities
- **Data Visualization**: Interactive price charts with zoom/pan capabilities
- **Stationarity Check**: Augmented Dickey-Fuller test results
- **Time Series Decomposition**: Separate plots for trend, seasonality, and residuals
- **Model Summary**: Detailed SARIMAX model statistics
- **Forecast Visualization**: Side-by-side comparison of actual vs predicted values

## 🔮 Future Scope
- Integration of LSTM neural networks for enhanced accuracy
- Sentiment analysis using news/social media data
- Expansion to cryptocurrency markets
- Portfolio optimization features
- Multi-currency support for global markets

## 📸 Sample Outputs
1. **Main Interface**: Interactive price chart with date selection
   ![Main Interface](https://github.com/digantk31/StockAI/blob/main/images/1-Main%20Interface.png)
2. **Decomposition Plots**: Visual breakdown of time series components
   ![Decomposition Plots](https://github.com/digantk31/StockAI/blob/main/images/2-Decomposition%20Plots.png)
3. **Forecast Comparison**: Overlay of actual vs predicted values
   ![Forecast Comparison](https://github.com/digantk31/StockAI/blob/main/images/3-Forecast%20Comparison.png)
4. **Model Summary**: Statistical summary of SARIMAX parameters
   ![Model Summary](https://github.com/digantk31/StockAI/blob/main/images/4-Model%20Summary.png)

## 🔗 Links
- **GitHub Repository**: [GitHub](https://github.com/digantk31/StockAI)
- **Deployed App**: [App](https://stockai-app.streamlit.app/)

## 🙏 Acknowledgements
Thank you for using StockAI! We appreciate any feedback and suggestions for further improvement.
