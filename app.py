<<<<<<< HEAD

import streamlit as st

# Page config MUST be the first Streamlit command
st.set_page_config(page_title="StockAI", layout="wide", page_icon="📈")

# Import Page Functions
from views.forecast_page import show_forecast_page
from views.portfolio_page import show_portfolio_page
from views.ai_page import show_ai_page
from views.trading_page import show_trading_page

# ============ MINIMAL CSS ENHANCEMENTS (works with Streamlit dark theme) ============
st.markdown("""
<style>
    /* Metric cards: subtle hover lift */
    [data-testid="stMetric"] {
        border-radius: 10px;
        padding: 14px;
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* Plotly chart container */
    [data-testid="stPlotlyChart"] {
        border-radius: 10px;
        padding: 4px;
    }
    
    /* Clean scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #555; border-radius: 3px; }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: rgba(255,255,255,0.1);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR BRANDING ============
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px;">
    <h1 style="font-size: 1.8rem; margin: 0; color: #4da6ff;">📈 StockAI</h1>
    <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 4px;">AI-Powered Stock Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Main Navigation
page = st.sidebar.radio("Navigate", ["Stock Forecast", "Portfolio Analysis", "Advanced AI", "Trading Center", "About"])

if page == "Stock Forecast":
    show_forecast_page()
elif page == "Portfolio Analysis":
    show_portfolio_page()
elif page == "Advanced AI":
    show_ai_page()
elif page == "Trading Center":
    show_trading_page()
elif page == "About":
    st.title("About StockAI")
    
    st.markdown("### 🚀 AI-Powered Stock Market Intelligence")
    st.markdown("StockAI uses AI models to analyze stocks, predict prices, and optimize your portfolio — all in one app.")
    
    # What This App Does
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Forecasting** — Predict future stock prices using time-series analysis")
    with col2:
        st.success("🧠 **AI Models** — Deep Learning, Neural Networks, FinBERT Sentiment Analysis")
    with col3:
        st.warning("💼 **Portfolio** — Find the best mix of stocks for maximum returns with minimum risk")
    
    st.write("---")
    
    st.write("### 👤 Author")
    st.markdown("**Digant Kathiriya**")
    
    st.write("---")
    st.warning("""
    ⚠️ **Disclaimer**: This app is built for **learning and academic purposes only**. 
    The predictions and analysis should **NOT** be used for real trading. 
    Stock markets are unpredictable, and no AI model can guarantee results.
    """)
    
    st.write("### 🔮 What Can Be Improved in Future")
    st.markdown("""
    - **Better AI Models** — Use more advanced language models (FinBERT/GPT) for reading news
    - **Smarter Predictions** — Use LSTM and GRU deep learning for better accuracy
    - **Live Data** — Connect to real-time stock feeds
    - **More Markets** — Support for US, Indian, and European stock exchanges
    """)

=======

import streamlit as st

# Page config MUST be the first Streamlit command
st.set_page_config(page_title="StockAI", layout="wide", page_icon="📈")

# Import Page Functions
from views.forecast_page import show_forecast_page
from views.portfolio_page import show_portfolio_page
from views.ai_page import show_ai_page

# ============ MINIMAL CSS ENHANCEMENTS (works with Streamlit dark theme) ============
st.markdown("""
<style>
    /* Metric cards: subtle hover lift */
    [data-testid="stMetric"] {
        border-radius: 10px;
        padding: 14px;
        transition: transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }
    
    /* Plotly chart container */
    [data-testid="stPlotlyChart"] {
        border-radius: 10px;
        padding: 4px;
    }
    
    /* Clean scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #555; border-radius: 3px; }
    
    /* Dividers */
    hr {
        border: none;
        height: 1px;
        background: rgba(255,255,255,0.1);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ SIDEBAR BRANDING ============
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 16px;">
    <h1 style="font-size: 1.8rem; margin: 0; color: #4da6ff;">📈 StockAI</h1>
    <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 4px;">AI-Powered Stock Intelligence</p>
</div>
""", unsafe_allow_html=True)

# Main Navigation
page = st.sidebar.radio("Navigate", ["Stock Forecast", "Portfolio Analysis", "Advanced AI", "About"])

if page == "Stock Forecast":
    show_forecast_page()
elif page == "Portfolio Analysis":
    show_portfolio_page()
elif page == "Advanced AI":
    show_ai_page()
elif page == "About":
    st.title("About StockAI")
    
    st.markdown("### 🚀 AI-Powered Stock Market Intelligence")
    st.markdown("StockAI uses AI models to analyze stocks, predict prices, and optimize your portfolio — all in one app.")
    
    # What This App Does
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Forecasting** — Predict future stock prices using time-series analysis")
    with col2:
        st.success("🧠 **AI Models** — Deep Learning, Neural Networks, FinBERT Sentiment Analysis")
    with col3:
        st.warning("💼 **Portfolio** — Find the best mix of stocks for maximum returns with minimum risk")
    
    st.write("---")
    
    st.write("### 👤 Author")
    st.markdown("**Digant Kathiriya**")
    
    st.write("---")
    st.warning("""
    ⚠️ **Disclaimer**: This app is built for **learning and academic purposes only**. 
    The predictions and analysis should **NOT** be used for real trading. 
    Stock markets are unpredictable, and no AI model can guarantee results.
    """)
    
    st.write("### 🔮 What Can Be Improved in Future")
    st.markdown("""
    - **Better AI Models** — Use more advanced language models (FinBERT/GPT) for reading news
    - **Smarter Predictions** — Use LSTM and GRU deep learning for better accuracy
    - **Live Data** — Connect to real-time stock feeds
    - **More Markets** — Support for US, Indian, and European stock exchanges
    """)

>>>>>>> 6386e94637a22f90201315ae3415d652ac7ba5f0
