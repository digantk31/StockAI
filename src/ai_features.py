
import yfinance as yf
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error, r2_score
import streamlit as st
import datetime
import warnings
warnings.filterwarnings('ignore')

class SentimentAnalyzer:
    """
    Analyzes news sentiment for a given stock ticker.
    """
    def __init__(self, ticker):
        self.ticker = ticker
    
    def _get_financial_sentiment(self, text):
        """
        Calculates sentiment using a hybrid approach: 
        TextBlob (General NLP) + Financial Lexicon (Domain Specific).
        Returns a score between -1 and 1.
        """
        # 1. Base Score from TextBlob
        blob = TextBlob(text)
        base_score = blob.sentiment.polarity
        
        # 2. Financial Lexicon Adjustment
        text_lower = text.lower()
        
        # Domain-specific terms
        bullish_terms = [
            'surge', 'jump', 'soar', 'rally', 'beat', 'gain', 'climb', 'up', 'rise', 
            'outperform', 'upgrade', 'buy', 'growth', 'profit', 'record', 'high', 
            'bull', 'positive', 'win', 'strong', 'boost', 'top', 'recover'
        ]
        
        bearish_terms = [
            'plunge', 'drop', 'fall', 'sink', 'miss', 'loss', 'decline', 'down', 
            'underperform', 'downgrade', 'sell', 'crash', 'correction', 'low', 
            'bear', 'negative', 'fail', 'weak', 'slump', 'worries', 'tumble', 
            'retreat', 'fear'
        ]
        
        score_adjustment = 0.0
        
        # Vectorized-style check (simple loop)
        for word in bullish_terms:
            if word in text_lower:
                score_adjustment += 0.2
                
        for word in bearish_terms:
            if word in text_lower:
                score_adjustment -= 0.2
                
        # Combine scores
        final_score = base_score + score_adjustment
        
        # Clamp between -1 and 1
        return max(-1.0, min(1.0, final_score))

    def get_news_sentiment(self):
        """
        Fetches news from Yahoo Finance and calculates average sentiment.
        Returns:
            DataFrame with news headlines and sentiment scores.
        """
        try:
            stock = yf.Ticker(self.ticker)
            news = stock.news
            
            if not news:
                return pd.DataFrame()
            
            data = []
            for item in news:
                # Handle both old and new yfinance news formats
                if isinstance(item, dict):
                    # Old format: {'title': '...', 'publisher': '...', 'link': '...'}
                    # New format: {'content': {'title': '...'}, 'link': '...'}
                    if 'content' in item:
                        content = item.get('content', {})
                        title = content.get('title', '')
                        publisher = content.get('provider', {}).get('displayName', '') if isinstance(content.get('provider'), dict) else ''
                        link = item.get('link', '')
                    else:
                        title = item.get('title', '')
                        publisher = item.get('publisher', '')
                        link = item.get('link', '')
                else:
                    continue
                
                # Analyze sentiment with advanced financial logic
                score = self._get_financial_sentiment(title)
                
                # Determine label with tighter bounds for "Neutral"
                sentiment_label = 'Neutral'
                if score > 0.05:
                    sentiment_label = 'Positive'
                elif score < -0.05:
                    sentiment_label = 'Negative'
                
                data.append({
                    'Title': title,
                    'Publisher': publisher,
                    'Sentiment Score': score,
                    'Sentiment': sentiment_label,
                    'Link': link
                })
            
            return pd.DataFrame(data)
        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return pd.DataFrame()

class NeuralNetForecaster:
    """
    Predicts stock prices using a Multi-Layer Perceptron (Neural Network).
    Includes Regularization to prevent Overfitting.
    """
    def __init__(self, data, look_back=60):
        self.data = data # Series or DataFrame with 'Close'
        self.look_back = look_back
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.test_score = 0.0 
        
    def prepare_data(self):
        # Convert to numpy array
        dataset = self.data.values.reshape(-1, 1)
        # Normalize
        self.scaled_data = self.scaler.fit_transform(dataset)
        
        # Split into X and y
        X, y = [], []
        for i in range(self.look_back, len(self.scaled_data)):
            X.append(self.scaled_data[i-self.look_back:i, 0])
            y.append(self.scaled_data[i, 0])
            
        return np.array(X), np.array(y)
    
    def build_and_train_model(self):
        # Neural Network Architecture with REGULARIZATION:
        # 1. hidden_layer_sizes=(50, 25): Simpler architecture than (100, 50) to prevent memorization.
        # 2. early_stopping=True: Stops training when validation score stops improving.
        # 3. alpha=0.01: L2 Regularization penalty to keep weights small.
        self.model = MLPRegressor(hidden_layer_sizes=(50, 25), 
                                  activation='relu', 
                                  solver='adam', 
                                  max_iter=500, 
                                  random_state=42,
                                  early_stopping=True,     # PREVENT OVERFITTING
                                  validation_fraction=0.1, # Data used for early stopping
                                  alpha=0.01)              # L2 Regularization
        
        X, y = self.prepare_data()
        
        # Split into Train/Test to calculate score (Last 10% as test)
        split_idx = int(len(X) * 0.9)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        self.model.fit(X_train, y_train)
        
        # Calculate R^2 Score on Test Set
        if len(X_test) > 0:
            self.test_score = self.model.score(X_test, y_test)
        else:
            self.test_score = self.model.score(X_train, y_train) # Fallback to train score
            
        # Refit on FULL data for better future prediction
        # Note: We still use early_stopping here internally
        self.model.fit(X, y)
        
        return self.test_score
        
    def predict_future(self, days=30):
        # Taking the last look_back days from data
        last_days = self.scaled_data[-self.look_back:]
        curr_input = last_days.reshape(1, -1) # Flatten for MLP
        
        future_predictions = []
        
        for _ in range(days):
            pred = self.model.predict(curr_input)
            future_predictions.append(pred[0])
            
            # Update input: remove first element, add new prediction
            new_input = np.append(curr_input[0][1:], pred)
            curr_input = new_input.reshape(1, -1)
            
        # Inverse transform
        future_predictions = np.array(future_predictions).reshape(-1, 1)
        return self.scaler.inverse_transform(future_predictions)


class TrendClassifier:
    """
    Predicts stock trend with accuracy metric.
    Includes Regularization to prevent Overfitting.
    """
    def __init__(self, data):
        self.data = data.copy()
        
    def add_indicators(self):
        # Ensure we have data
        if len(self.data) < 14:
            return self.data
            
        df = self.data.to_frame() if isinstance(self.data, pd.Series) else self.data
        if 'Close' not in df.columns:
             # Assume single column is close
             df.columns = ['Close']
        
        # 1. RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 2. SMA (Simple Moving Average)
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # 3. Returns
        df['Returns'] = df['Close'].pct_change()
        
        # Target: 1 if tomorrow's price > today's price, else 0
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        return df.dropna()
        
    def predict_trend(self):
        df = self.add_indicators()
    
        if len(df) < 50:
            return None, 0, 0, None
            
        features = ['RSI', 'SMA_20', 'SMA_50', 'Returns', 'Close']
        
        X = df[features]
        y = df['Target']
        
        # Training Data: All rows except the last one (since last one has unknown target)
        X_full = X.iloc[:-1]
        y_full = y.iloc[:-1]
        
        # Split for Accuracy Calculation (80% Train, 20% Test)
        split_idx = int(len(X_full) * 0.8)
        X_train_sub = X_full.iloc[:split_idx]
        y_train_sub = y_full.iloc[:split_idx]
        X_test_sub = X_full.iloc[split_idx:]
        y_test_sub = y_full.iloc[split_idx:]
        
        # Train on Subset to get Accuracy Score
        # REGULARIZATION ADDED HERE:
        # max_depth=10: Prevents the tree from growing too deep (memorizing noise).
        # min_samples_split=20: Requires 20 samples to split a node (prevents overly specific branches).
        model = RandomForestClassifier(n_estimators=100, 
                                       min_samples_split=20, 
                                       max_depth=10, 
                                       random_state=42)
        model.fit(X_train_sub, y_train_sub)
        
        accuracy = 0.0
        if len(X_test_sub) > 0:
            y_pred = model.predict(X_test_sub)
            accuracy = accuracy_score(y_test_sub, y_pred)
        
        # Now Train on FULL Data for the Real Prediction
        model.fit(X_full, y_full)
        
        # Feature Importances
        feature_importance = pd.DataFrame({
            'Feature': features,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        # Prediction Data: The last row (represents "Today")
        X_today = X.iloc[[-1]]
        
        # Predict
        prediction = model.predict(X_today)[0]
        probability = model.predict_proba(X_today)[0][1] # Probability of Class 1 (Up)
        
        signal = "Bullish (Buy)" if prediction == 1 else "Bearish (Sell)"
        confidence = probability if prediction == 1 else (1 - probability)
        
        return signal, confidence, accuracy, feature_importance


class LSTMForecaster:
    """
    Predicts stock prices using LSTM (Long Short-Term Memory) Deep Learning.
    Falls back to Gradient Boosting with Sequential Features if TensorFlow 
    is not available (e.g., Python 3.14+).
    
    The fallback model uses temporal feature engineering (lagged values, 
    rolling statistics, momentum) to capture sequential patterns — 
    similar to how LSTM captures temporal dependencies.
    """
    def __init__(self, data, look_back=60):
        self.data = data
        self.look_back = look_back
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.test_score = 0.0
        self.test_rmse = 0.0
        self.test_mae = 0.0
        self.scaled_data = None
        self.use_lstm = False
        self.model_name = ""
        
    def _check_tensorflow(self):
        """Check if TensorFlow is available."""
        try:
            import tensorflow
            return True
        except ImportError:
            return False
    
    def _prepare_sequential_features(self, data_array):
        """
        Create temporal features that capture sequential patterns
        (similar to LSTM's memory mechanism).
        """
        from sklearn.preprocessing import StandardScaler
        
        df = pd.DataFrame(data_array, columns=['price'])
        
        # Lagged features (like LSTM's hidden state memory)
        for lag in [1, 3, 5, 7, 14, 21, 30]:
            if lag < len(df):
                df[f'lag_{lag}'] = df['price'].shift(lag)
        
        # Rolling statistics (like LSTM's cell state)
        for window in [5, 10, 20, 30]:
            if window < len(df):
                df[f'rolling_mean_{window}'] = df['price'].rolling(window).mean()
                df[f'rolling_std_{window}'] = df['price'].rolling(window).std()
        
        # Momentum features (like LSTM's forget gate)
        for period in [5, 10, 20]:
            if period < len(df):
                df[f'momentum_{period}'] = df['price'] - df['price'].shift(period)
                df[f'roc_{period}'] = df['price'].pct_change(period)
        
        # Trend features
        df['price_diff'] = df['price'].diff()
        df['price_diff2'] = df['price'].diff().diff()
        
        df = df.dropna()
        return df
    
    def prepare_data(self):
        """Prepare and scale data."""
        dataset = self.data.values.reshape(-1, 1)
        self.scaled_data = self.scaler.fit_transform(dataset)
        
        if self.use_lstm:
            # LSTM format
            X, y = [], []
            for i in range(self.look_back, len(self.scaled_data)):
                X.append(self.scaled_data[i-self.look_back:i, 0])
                y.append(self.scaled_data[i, 0])
            X = np.array(X)
            y = np.array(y)
            X = X.reshape(X.shape[0], X.shape[1], 1)
            return X, y
        else:
            # Sequential features format
            df = self._prepare_sequential_features(self.scaled_data.flatten())
            feature_cols = [c for c in df.columns if c != 'price']
            X = df[feature_cols].values
            y = df['price'].values
            return X, y
        
    def build_and_train_model(self):
        """
        Build and train the model.
        Uses LSTM if TensorFlow available, else GradientBoosting with sequential features.
        Returns: dict with test metrics (r2, rmse, mae)
        """
        self.use_lstm = self._check_tensorflow()
        
        if self.use_lstm:
            return self._train_lstm()
        else:
            return self._train_gradient_boosting()
    
    def _train_lstm(self):
        """Train real LSTM model using TensorFlow/Keras."""
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import LSTM, Dense, Dropout
            from tensorflow.keras.callbacks import EarlyStopping
        except ImportError:
            self.use_lstm = False
            return self._train_gradient_boosting()
        
        self.model_name = "LSTM (Deep Learning)"
        X, y = self.prepare_data()
        
        split_idx = int(len(X) * 0.9)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        self.model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(self.look_back, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mse')
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        self.model.fit(X_train, y_train, epochs=50, batch_size=32,
                       validation_split=0.1, callbacks=[early_stop], verbose=0)
        
        if len(X_test) > 0:
            y_pred_scaled = self.model.predict(X_test, verbose=0).flatten()
            y_test_real = self.scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
            y_pred_real = self.scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
            self.test_score = r2_score(y_test_real, y_pred_real)
            self.test_rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))
            self.test_mae = mean_absolute_error(y_test_real, y_pred_real)
        
        self.model.fit(X, y, epochs=20, batch_size=32, verbose=0)
        return {'r2': self.test_score, 'rmse': self.test_rmse, 'mae': self.test_mae}
    
    def _train_gradient_boosting(self):
        """
        Train GradientBoosting with sequential features as LSTM fallback.
        Uses temporal feature engineering to capture sequential patterns.
        """
        from sklearn.ensemble import GradientBoostingRegressor
        
        self.model_name = "Gradient Boosting (Sequential Features)"
        self.use_lstm = False
        X, y = self.prepare_data()
        
        split_idx = int(len(X) * 0.9)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # GradientBoosting with regularization
        self.model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,          # Stochastic gradient boosting
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        
        self.model.fit(X_train, y_train)
        
        if len(X_test) > 0:
            y_pred_scaled = self.model.predict(X_test)
            y_test_real = self.scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
            y_pred_real = self.scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
            self.test_score = r2_score(y_test_real, y_pred_real)
            self.test_rmse = np.sqrt(mean_squared_error(y_test_real, y_pred_real))
            self.test_mae = mean_absolute_error(y_test_real, y_pred_real)
        
        # Refit on full data
        self.model.fit(X, y)
        return {'r2': self.test_score, 'rmse': self.test_rmse, 'mae': self.test_mae}
    
    def predict_future(self, days=30):
        """Predict future prices."""
        if self.use_lstm:
            return self._predict_lstm(days)
        else:
            return self._predict_gb(days)
    
    def _predict_lstm(self, days):
        """Predict using LSTM model."""
        last_days = self.scaled_data[-self.look_back:]
        curr_input = last_days.reshape(1, self.look_back, 1)
        
        future_predictions = []
        for _ in range(days):
            pred = self.model.predict(curr_input, verbose=0)
            future_predictions.append(pred[0, 0])
            new_input = np.append(curr_input[0, 1:, 0], pred[0, 0])
            curr_input = new_input.reshape(1, self.look_back, 1)
        
        future_predictions = np.array(future_predictions).reshape(-1, 1)
        return self.scaler.inverse_transform(future_predictions)
    
    def _predict_gb(self, days):
        """Predict using GradientBoosting with sequential feature generation."""
        # Start with the scaled data we have
        extended_data = list(self.scaled_data.flatten())
        
        future_predictions = []
        for _ in range(days):
            # Build features for the latest point
            df = self._prepare_sequential_features(np.array(extended_data))
            feature_cols = [c for c in df.columns if c != 'price']
            last_features = df[feature_cols].iloc[[-1]].values
            
            pred = self.model.predict(last_features)[0]
            future_predictions.append(pred)
            extended_data.append(pred)
        
        future_predictions = np.array(future_predictions).reshape(-1, 1)
        return self.scaler.inverse_transform(future_predictions)


class FinBERTAnalyzer:
    """
    Advanced financial sentiment analysis using FinBERT (Transformer model).
    Falls back to TextBlob + Financial Lexicon if transformers is not installed.
    """
    def __init__(self, ticker):
        self.ticker = ticker
        self.model_name = "ProsusAI/finbert"
        self.pipeline = None
        self.use_finbert = False
        self._init_model()
    
    def _init_model(self):
        """Try to load FinBERT, fallback to TextBlob."""
        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "sentiment-analysis", 
                model=self.model_name,
                tokenizer=self.model_name,
                top_k=None
            )
            self.use_finbert = True
        except Exception:
            self.use_finbert = False
    
    def _analyze_text(self, text):
        """
        Analyze sentiment of a single text.
        Returns: (score, label)
        """
        if self.use_finbert and self.pipeline:
            try:
                result = self.pipeline(text[:512])  # FinBERT max 512 tokens
                if result and len(result) > 0:
                    # result is a list of list of dicts
                    scores = result[0] if isinstance(result[0], list) else result
                    
                    # Convert FinBERT labels to score
                    score = 0.0
                    for item in scores:
                        label = item['label'].lower()
                        if label == 'positive':
                            score += item['score']
                        elif label == 'negative':
                            score -= item['score']
                    
                    label = 'Positive' if score > 0.05 else ('Negative' if score < -0.05 else 'Neutral')
                    return score, label
            except Exception:
                pass
        
        # Fallback: TextBlob + Financial Lexicon
        return self._textblob_fallback(text)
    
    def _textblob_fallback(self, text):
        """TextBlob + financial lexicon as fallback."""
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        
        text_lower = text.lower()
        bullish = ['surge', 'jump', 'soar', 'rally', 'beat', 'gain', 'climb', 'rise', 
                   'outperform', 'upgrade', 'buy', 'growth', 'profit', 'record', 'high',
                   'bull', 'positive', 'strong', 'boost', 'recover']
        bearish = ['plunge', 'drop', 'fall', 'sink', 'miss', 'loss', 'decline', 'down',
                   'underperform', 'downgrade', 'sell', 'crash', 'correction', 'low',
                   'bear', 'negative', 'weak', 'slump', 'tumble', 'fear']
        
        for word in bullish:
            if word in text_lower:
                score += 0.2
        for word in bearish:
            if word in text_lower:
                score -= 0.2
        
        score = max(-1.0, min(1.0, score))
        label = 'Positive' if score > 0.05 else ('Negative' if score < -0.05 else 'Neutral')
        return score, label
    
    def get_news_sentiment(self):
        """
        Fetch news and analyze sentiment using FinBERT (or TextBlob fallback).
        Returns: DataFrame and model_used string.
        """
        try:
            stock = yf.Ticker(self.ticker)
            news = stock.news
            
            if not news:
                return pd.DataFrame(), self._model_used()
            
            data = []
            for item in news:
                if isinstance(item, dict):
                    if 'content' in item:
                        content = item.get('content', {})
                        title = content.get('title', '')
                        publisher = content.get('provider', {}).get('displayName', '') if isinstance(content.get('provider'), dict) else ''
                        link = item.get('link', '')
                    else:
                        title = item.get('title', '')
                        publisher = item.get('publisher', '')
                        link = item.get('link', '')
                else:
                    continue
                
                if not title:
                    continue
                    
                score, label = self._analyze_text(title)
                data.append({
                    'Title': title,
                    'Publisher': publisher,
                    'Sentiment Score': round(score, 3),
                    'Sentiment': label,
                    'Link': link
                })
            
            return pd.DataFrame(data), self._model_used()
        except Exception as e:
            st.error(f"Error fetching news: {e}")
            return pd.DataFrame(), self._model_used()
    
    def _model_used(self):
        """Return which model is being used."""
        return "FinBERT (Transformer)" if self.use_finbert else "TextBlob + Financial Lexicon"
