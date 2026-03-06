
import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go
import plotly.express as px
from src.ai_features import (
    SentimentAnalyzer, NeuralNetForecaster, TrendClassifier,
    LSTMForecaster, FinBERTAnalyzer
)

def show_ai_page():
    st.title("Advanced AI Insights 🤖")
    st.markdown("Use **AI Models** to analyze news sentiment, predict stock trends, and forecast future prices.")
    st.info("ℹ️ This page uses multiple AI models to give you different perspectives on a stock. All predictions are for learning purposes only.")
    
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL").upper()
    
    if st.button("Analyze Stock"):
        # --- VALIDATION STEP ---
        with st.spinner(f"Verifying ticker {ticker}..."):
            check_data = yf.download(ticker, period="1d", progress=False)
            if check_data.empty:
                st.error(f"❌ **Invalid Ticker '{ticker}'**: Please write the correct ticker symbol (e.g., AAPL, RELIANCE.NS).")
                return
        # -----------------------

        # 1. Sentiment Analysis (FinBERT with TextBlob fallback)
        st.subheader("1. What's the Market Saying? (News Sentiment)")
        with st.spinner("Reading latest news..."):
            # Try FinBERT first
            finbert_analyzer = FinBERTAnalyzer(ticker)
            sentiment_df, model_used = finbert_analyzer.get_news_sentiment()
            
            st.caption(f"🔬 **AI Model Used**: {model_used}")
            
            if not sentiment_df.empty:
                avg_score = sentiment_df['Sentiment Score'].mean()
                if avg_score > 0.05:
                    st.success(f"Overall Sentiment: Positive ({avg_score:.2f})")
                elif avg_score < -0.05:
                    st.error(f"Overall Sentiment: Negative ({avg_score:.2f})")
                else:
                    st.info(f"Overall Sentiment: Neutral ({avg_score:.2f})")
                    
                st.dataframe(sentiment_df[['Title', 'Sentiment', 'Sentiment Score']])
                
                # Sentiment distribution chart
                sentiment_counts = sentiment_df['Sentiment'].value_counts()
                fig_sent = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                                  title="Sentiment Distribution", 
                                  color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'})
                st.plotly_chart(fig_sent)
            else:
                st.write("No recent news found for sentiment analysis.")

        # 2. AI Trade Signal + Feature Importance
        st.subheader("2. Should You Buy or Sell? (AI Trade Signal)")
        st.markdown("*The AI looks at price patterns and momentum to predict tomorrow's trend.*")
        
        with st.spinner("Calculating indicators and predicting trend..."):
            try:
                # Fetch data
                end = datetime.date.today()
                start = end - datetime.timedelta(days=365*2)
                data = yf.download(ticker, start=start, end=end)
                
                if not data.empty:
                    # Handle columns
                    if isinstance(data.columns, pd.MultiIndex):
                        if 'Close' in data.columns.get_level_values(0):
                             data = data['Close']
                        else:
                             data = data.iloc[:, 0]
                    elif 'Close' in data.columns:
                        data = data['Close']
                    else:
                        data = data.iloc[:,0] # Fallback
                    
                    classifier = TrendClassifier(data)
                    signal, confidence, accuracy, feature_importance = classifier.predict_trend()
                    
                    if signal:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tomorrow's Prediction", signal)
                        with col2:
                            st.metric("How Confident", f"{confidence*100:.1f}%")
                        with col3:
                            st.metric("Past Accuracy", f"{accuracy*100:.1f}%", help="How often the AI was right on past data")
                            
                        # Signal logic
                        if "Bullish" in signal and confidence > 0.6:
                            st.success("Strong Buy Signal Detected! 🚀")
                        elif "Bearish" in signal and confidence > 0.6:
                            st.error("Strong Sell Signal Detected! 📉")
                        else:
                            st.info("Weak Signal - Market Indecisive.")
                            
                        if accuracy < 0.5:
                            st.warning("⚠️ Note: Historical accuracy is low (<50%). Treat prediction with caution.")
                        
                        # Feature Importance Chart
                        if feature_importance is not None:
                            st.write("#### What Matters Most? (Feature Importance)")
                            st.markdown("*This chart shows which factors the AI relies on most to make its prediction.*")
                            fig_fi = px.bar(feature_importance, x='Importance', y='Feature', 
                                           orientation='h', title='Random Forest Feature Importance',
                                           color='Importance', color_continuous_scale='Viridis')
                            fig_fi.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
                            st.plotly_chart(fig_fi)
                            
                    else:
                        st.warning("Not enough data to generate a signal.")
                else:
                    st.error("Insufficient data.")
            except Exception as e:
                st.error(f"Signal Error: {e}")

        # 3. MLP Neural Network Forecasting
        st.subheader("3. Price Forecast — Neural Network (MLP)")
        st.markdown("*Training a basic neural network to learn price patterns and predict the next 30 days...*")
        
        mlp_metrics = {}
        mlp_predictions = None
        
        with st.spinner("Training MLP model..."):
            try:
                if 'data' not in locals() or data.empty:
                     data = yf.download(ticker, start=start, end=end)
                
                if not data.empty:
                    # Train MLP Model
                    forecaster = NeuralNetForecaster(data, look_back=60)
                    r2_score_mlp = forecaster.build_and_train_model()
                    
                    # Predict Next 30 Days
                    mlp_predictions = forecaster.predict_future(days=30)
                    
                    # Store metrics for comparison
                    mlp_metrics = {
                        'R² Score': r2_score_mlp,
                        'Model': 'MLP'
                    }
                    
                    st.metric("Prediction Accuracy (R²)", f"{r2_score_mlp:.4f}", help="1.0 = perfect prediction, 0 = random guess")
                    
                else:
                    st.error("Insufficient data for training.")
            
            except Exception as e:
                import traceback
                st.error(f"MLP Error: {e}")
                st.text(traceback.format_exc())

        # 4. LSTM Deep Learning Forecasting (NEW!)
        st.subheader("4. Price Forecast — Advanced Model")
        st.markdown("*Training a more powerful AI model that can detect time-based patterns in stock data...*")
        
        lstm_metrics = {}
        lstm_predictions = None
        
        with st.spinner("Training LSTM model (this may take 1-2 minutes)..."):
            try:
                if not data.empty:
                    lstm_forecaster = LSTMForecaster(data, look_back=60)
                    lstm_result = lstm_forecaster.build_and_train_model()
                    
                    if lstm_result:
                        lstm_predictions = lstm_forecaster.predict_future(days=30)
                        lstm_metrics = lstm_result
                        
                        st.caption(f"🔬 **Model Used**: {lstm_forecaster.model_name}")
                        
                        col_l1, col_l2, col_l3 = st.columns(3)
                        with col_l1:
                            st.metric("Prediction Accuracy (R²)", f"{lstm_result['r2']:.4f}", help="1.0 = perfect, 0 = random")
                        with col_l2:
                            st.metric("Average Error (RMSE)", f"{lstm_result['rmse']:.2f}", help="Lower = better predictions")
                        with col_l3:
                            st.metric("Typical Error (MAE)", f"{lstm_result['mae']:.2f}", help="Average price difference from actual")
                    else:
                        st.warning("LSTM training failed. Make sure TensorFlow is installed: `pip install tensorflow`")
                        
            except Exception as e:
                import traceback
                st.error(f"LSTM Error: {e}")
                st.text(traceback.format_exc())

        # 5. Model Comparison & Combined Forecast Chart
        st.write("---")
        st.subheader("5. Which AI Model is Better?")
        st.markdown("*Comparing both AI models side-by-side to see which one predicts better for this stock.*")
        
        # Create future dates
        if not data.empty:
            last_date = data.index[-1]
            future_dates = [last_date + datetime.timedelta(days=x) for x in range(1, 31)]
            
            # Combined Forecast Chart
            fig_compare = go.Figure()
            
            # Historical Data (Last 90 days)
            vals = data.values if isinstance(data, pd.Series) else data.iloc[:,0].values
            fig_compare.add_trace(go.Scatter(
                x=data.index[-90:], y=vals[-90:],
                mode='lines', name='Historical Price', line=dict(color='blue', width=2)
            ))
            
            # MLP Forecast
            if mlp_predictions is not None:
                fig_compare.add_trace(go.Scatter(
                    x=future_dates, y=mlp_predictions.flatten(),
                    mode='lines+markers', name='MLP Forecast',
                    line=dict(color='purple', dash='dot', width=2)
                ))
            
            # LSTM Forecast
            if lstm_predictions is not None:
                fig_compare.add_trace(go.Scatter(
                    x=future_dates, y=lstm_predictions.flatten(),
                    mode='lines+markers', name='LSTM Forecast',
                    line=dict(color='orange', dash='dash', width=2)
                ))
            
            fig_compare.update_layout(
                title=f"30-Day Forecast Comparison for {ticker}",
                xaxis_title="Date", yaxis_title="Price",
                height=500
            )
            st.plotly_chart(fig_compare)
            
            # Comparison Table
            st.write("#### Model Performance Comparison")
            st.markdown("*Higher R² = better predictions. Lower errors = more accurate.*")
            
            comparison_data = []
            if mlp_metrics:
                comparison_data.append({
                    'Model': 'MLP (Neural Network)',
                    'Type': 'Shallow Neural Network',
                    'R² Score': f"{mlp_metrics.get('R² Score', 'N/A'):.4f}" if isinstance(mlp_metrics.get('R² Score'), float) else 'N/A',
                    'Architecture': '2 Hidden Layers (50, 25)',
                    'Regularization': 'L2 + Early Stopping'
                })
            if lstm_metrics:
                model_label = getattr(lstm_forecaster, 'model_name', 'Sequential Model') if 'lstm_forecaster' in dir() else 'Sequential Model'
                comparison_data.append({
                    'Model': model_label,
                    'Type': 'Ensemble (Temporal Features)' if 'Gradient' in model_label else 'Recurrent Neural Network',
                    'R² Score': f"{lstm_metrics.get('r2', 'N/A'):.4f}" if isinstance(lstm_metrics.get('r2'), float) else 'N/A',
                    'Architecture': '200 Trees, depth=5, sequential features' if 'Gradient' in model_label else '2 LSTM Layers (50, 50) + Dense',
                    'Regularization': 'Subsampling + Min Samples' if 'Gradient' in model_label else 'Dropout (0.2) + Early Stopping'
                })
            
            if comparison_data:
                st.table(pd.DataFrame(comparison_data).set_index('Model'))
                
                # Determine winner
                if mlp_metrics and lstm_metrics:
                    mlp_r2 = mlp_metrics.get('R² Score', 0)
                    lstm_r2 = lstm_metrics.get('r2', 0)
                    if isinstance(mlp_r2, (int, float)) and isinstance(lstm_r2, (int, float)):
                        if lstm_r2 > mlp_r2:
                            st.success(f"🏆 **LSTM outperforms MLP** (R² {lstm_r2:.4f} vs {mlp_r2:.4f}) — Deep learning captures temporal patterns better.")
                        elif mlp_r2 > lstm_r2:
                            st.success(f"🏆 **MLP outperforms LSTM** (R² {mlp_r2:.4f} vs {lstm_r2:.4f}) — Simpler model works better for this stock.")
                        else:
                            st.info("Both models perform equally.")
