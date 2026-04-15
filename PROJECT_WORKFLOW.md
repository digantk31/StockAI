# StockAI — Complete Project Workflow Guide
> **Use this to understand and explain every concept in your exam.**
> All examples use **Apple (AAPL)** as the stock.

---

# PART 1: GLOSSARY — Every Term Explained Simply

> If the panel asks _"What does X mean?"_ — find it here.

---

### General Terms

**API (Application Programming Interface)**
A way for our app to talk to another service. We use Yahoo Finance API to ask "Give me AAPL prices" and it sends the data back. Think of it like ordering food from a restaurant — you don't cook, you just ask and receive.

**Ticker Symbol**
A short code for a company's stock. AAPL = Apple, TCS.NS = TCS on Indian exchange, RELIANCE.NS = Reliance.

**Time Series**
Any data collected over time in order. Stock prices day by day = time series. The ORDER matters — Monday comes before Tuesday.

**Training Data**
The data we SHOW to our AI model so it can learn patterns. Like showing a student solved examples before an exam.

**Testing Data**
Data we HIDE from the model and use AFTER training to check if it actually learned anything. Like the actual exam paper.

**Overfitting**
When the model memorizes training data instead of learning patterns. Like a student who memorizes answers but can't solve new questions. Our model would score 99% on training data but fail on new data.

**Regularization**
Techniques to PREVENT overfitting. We use:
- **Early Stopping** — Stop training when performance on validation data starts getting worse
- **L2 (Ridge)** — Penalize large weights so the model stays simple
- **Dropout** — Randomly "turn off" some neurons during training so the model doesn't rely on any single neuron
- **max_depth** — Limit how deep decision trees can grow

**Normalization / Scaling**
Converting data to a 0-1 range using MinMaxScaler.
```
Scaled Value = (Value - Minimum) / (Maximum - Minimum)

Example: AAPL price = $180, Min = $120, Max = $200
Scaled = (180 - 120) / (200 - 120) = 60/80 = 0.75
```
Why? AI models work better when all numbers are in a similar range.

---

### Statistical Terms

**Stationarity**
A time series is "stationary" if its average and spread stay roughly the same over time. Stock prices usually go UP over time → NOT stationary. We need to make it stationary (by differencing) before SARIMAX can work.

**ADF Test (Augmented Dickey-Fuller Test)**
A mathematical test that checks: "Is this data stationary?"
- Result: p-value < 0.05 → **YES, it's stationary** ✅
- Result: p-value > 0.05 → **NO, it's not stationary** ❌ (need differencing)

**Differencing**
Subtracting each value from the previous one to remove the trend.
```
Original:     100, 105, 108, 115
After diff:   +5,  +3,  +7        ← Now it's about CHANGES, not levels
```
The `d` parameter in SARIMAX controls how many times we difference.

**Seasonal Decomposition**
Breaking a price series into 3 parts:
```
Price = Trend + Seasonality + Noise

Trend       = Overall direction (going up or down over months)
Seasonality = Repeating pattern (e.g., prices often dip in September)
Noise       = Random ups and downs that have no pattern
```

**Standard Deviation (σ)**
Measures how spread out the data is. In finance, this IS the risk (volatility).
```
Small std dev = Prices are stable = Low risk
Large std dev = Prices swing wildly = High risk
```

**Covariance**
Measures how two stocks move TOGETHER.
```
Positive covariance → When AAPL goes up, TCS also tends to go up
Negative covariance → When AAPL goes up, TCS tends to go down
Zero covariance → No relationship
```

**Correlation**
Same as covariance but SCALED to -1 to +1 range (easier to understand).
```
+1.0 = Perfect together (bad for diversification)
 0.0 = No relationship (good for diversification)
-1.0 = Perfect opposites (best for diversification)
```

---

### AI / ML Terms

**Machine Learning (ML)**
Teaching a computer to find patterns in data WITHOUT explicitly programming the rules. We show it examples, and it learns.

**Deep Learning**
A subset of ML that uses neural networks with MULTIPLE layers. "Deep" = many layers stacked.

**Neural Network**
Inspired by the human brain. Made of "neurons" organized in layers:
```
Input Layer → Hidden Layer(s) → Output Layer

Each neuron:
1. Takes inputs
2. Multiplies by weights
3. Adds bias
4. Passes through activation function
5. Sends output to next layer
```

**Neuron (Node)**
One processing unit. It does: `output = activation(w₁x₁ + w₂x₂ + ... + bias)`

**Weights**
Numbers that the model learns during training. They decide how important each input is. Training = finding the best weights.

**Bias**
An extra number added to help the model fit data better. Like the `c` in `y = mx + c`.

**Activation Function**
Decides if a neuron should "fire" or not.
- **ReLU** (Rectified Linear Unit): `output = max(0, input)`. If input is negative, output 0. If positive, pass it through. Simple and fast. **We use this in MLP.**
- **Sigmoid (σ)**: Squashes input to 0-1 range. Used in LSTM gates.
- **Tanh**: Squashes input to -1 to +1 range. Used in LSTM cell state.

**Epoch**
One complete pass through the entire training data. Like reading a textbook once = 1 epoch. We typically train for 50 epochs.

**Batch Size**
How many data points the model looks at before updating weights. We use 32.
```
500 data points, batch_size=32
→ 500/32 ≈ 16 weight updates per epoch
```

**Learning Rate**
How big a step the model takes when adjusting weights. Too high = keeps overshooting. Too low = takes forever to learn. We use `adam` optimizer which automatically adjusts this.

**Loss Function**
Measures how WRONG the model is. We minimize this during training.
- **MSE (Mean Squared Error)**: Average of (actual - predicted)². We use this for LSTM.

**Optimizer (Adam)**
The algorithm that updates weights to reduce loss. Adam = "Adaptive Moment Estimation" — it adjusts learning rate for each weight automatically. It's the most popular optimizer in deep learning.

**Validation Split**
10% of training data set aside to check for overfitting during training. If training loss goes down but validation loss goes UP → overfitting → early stopping triggers.

---

### Specific Model Terms

**MLP (Multi-Layer Perceptron)**
The simplest neural network. All neurons in one layer connect to ALL neurons in the next layer (fully connected). It treats all inputs equally — doesn't understand time order.

```
OUR MLP ARCHITECTURE:
Input (60 past prices) → Dense(50, ReLU) → Dense(25, ReLU) → Output(1 price)

Total: 2 hidden layers
Regularization: L2 (alpha=0.01) + Early Stopping
```

*Panel Q: "Why only 2 hidden layers?"*
> More layers = more parameters = more overfitting risk. With stock data (which is noisy), a simpler model generalizes better. We tried (100, 50) but found (50, 25) gives better test accuracy.

---

**LSTM (Long Short-Term Memory)**
A special type of neural network designed for SEQUENCES (time-ordered data). It can "remember" important past information and "forget" unimportant details.

**Why LSTM is better than MLP for stocks:**
```
MLP sees: [150, 155, 160, 158, 162] → treats all 5 prices as EQUAL inputs
LSTM sees: 150 → then 155 → then 160 → then 158 → then 162 → SEQUENCE
                                                                 ↑
                                                    Remembers the upward trend
```

**The 3 Gates of LSTM (explained like a student studying):**
```
📘 Forget Gate: "Should I forget what I studied yesterday?"
   → Decides which old information is no longer useful
   → Formula: f = σ(W × [old_output, new_input] + bias)
   → Output: 0 = forget completely, 1 = remember everything

📗 Input Gate: "What new information should I learn today?"
   → Decides which new information is worth storing
   → Formula: i = σ(W × [old_output, new_input] + bias)

📙 Output Gate: "What should I write in the exam (output)?"
   → Decides what to output based on current memory
   → Formula: o = σ(W × [old_output, new_input] + bias)

📦 Cell State (Memory):
   → New Memory = (Forget × Old Memory) + (Input × New Info)
   → This is the "long-term memory" that flows through time
```

```
OUR LSTM ARCHITECTURE:
Input(60,1) → LSTM(50) → Dropout(0.2) → LSTM(50) → Dropout(0.2) → Dense(25) → Output(1)

Dropout(0.2) = Randomly turn off 20% of neurons each training step (prevents overfitting)
```

*Panel Q: "What is Dropout?"*
> During each training step, we randomly "switch off" 20% of neurons. This forces the remaining neurons to learn independently, preventing the model from relying too much on any single neuron. It's like studying in a group — if one friend is absent, the others should still know the material.

---

**Random Forest**
An "ensemble" of 100 decision trees. Each tree votes on the prediction, and we take the majority.

```
How a Decision Tree works (simplified for our stock prediction):

                    RSI > 70?
                   /        \
                 Yes          No
                /              \
          SMA_20 > SMA_50?    Returns > 0?
           /        \          /        \
        SELL       BUY      SELL       BUY
```

**Why "Random"?**
Each tree sees a RANDOM subset of data and features, so they make different mistakes. When we average 100 trees, the random errors cancel out → better overall prediction.

**Feature Importance**
After training, Random Forest can tell us WHICH features were most useful:
```
Example output:
  Close      → 35% importance (most useful)
  RSI        → 25% importance
  SMA_20     → 20% importance
  SMA_50     → 12% importance
  Returns    → 8% importance (least useful)
```

---

**GradientBoosting (LSTM Fallback)**
Instead of random parallel trees (Random Forest), this builds trees ONE BY ONE, where each new tree fixes the mistakes of the previous ones.

```
Tree 1: Makes predictions → Has errors
Tree 2: Trained on Tree 1's ERRORS → Fixes some mistakes
Tree 3: Trained on remaining errors → Fixes more
... (200 trees)
Final: Combine all → Very accurate
```

We add "temporal features" to make it understand time:
- **Lagged prices**: What was the price 1, 3, 7, 14, 30 days ago?
- **Rolling averages**: What's the average price over last 5, 10, 20 days?
- **Momentum**: How much did the price change over last 5, 10, 20 days?

---

**FinBERT (Financial BERT)**
A Transformer-based AI model specifically trained to understand FINANCIAL language.

```
Normal NLP (TextBlob):  "The market is bearish" → Doesn't know "bearish" is negative
FinBERT:                "The market is bearish" → KNOWS "bearish" means prices will fall
```

**BERT** = Bidirectional Encoder Representations from Transformers
- Reads text BOTH left-to-right AND right-to-left
- Understands context: "Apple stock rose" (finance) vs "Apple fell from tree" (fruit)
- FinBERT was further trained on 50,000+ financial news articles

*Panel Q: "What is a Transformer?"*
> A Transformer is a deep learning architecture that uses "attention" — it can focus on the most important words in a sentence. Instead of reading word by word (like LSTM), it sees ALL words at once and learns which words relate to which. BERT, GPT, FinBERT are all Transformer models.

---

### Portfolio Terms

**Portfolio**
A collection of stocks you own. Example: 40% AAPL + 30% TCS + 30% RELIANCE = your portfolio.

**Diversification**
Spreading money across different stocks to reduce risk. If one stock falls, others might rise, balancing your losses.

**Modern Portfolio Theory (MPT)**
A mathematical framework (by Harry Markowitz, Nobel Prize 1990) that says: For any level of risk, there is ONE portfolio that gives the MAXIMUM return. The set of all such best portfolios forms the Efficient Frontier.

**Sharpe Ratio**
"Am I being rewarded enough for the risk I'm taking?"
```
Sharpe = (Portfolio Return - Bank FD Rate) / Risk

Example: Return = 18%, FD Rate = 6%, Risk = 10%
Sharpe = (18-6)/10 = 1.2

Sharpe > 1  = Good
Sharpe > 2  = Very good
Sharpe < 0  = Losing money (worse than FD)
```

**Efficient Frontier**
A curve on a graph where:
- X-axis = Risk (Volatility)
- Y-axis = Return

Any portfolio ON the curve is optimal. Below the curve = you can do better. Above the curve = impossible.

**Monte Carlo Simulation**
Generate 1000+ random portfolios by randomly assigning weights to stocks, calculate return and risk for each, then plot them all. The upper edge = Efficient Frontier.

**Maximum Drawdown**
The biggest peak-to-valley loss in your portfolio's history.
```
Portfolio value: 100 → 120 → 95 → 110
Peak = 120, Trough = 95
Drawdown = (120 - 95) / 120 = 20.8%
Meaning: At worst, you would have lost 20.8% from your highest point.
```

---

# PART 2: COMPLETE WORKFLOW (With AAPL Example)

## 🔄 Overall Architecture

```
User opens app (streamlit run app.py)
         ↓
Sidebar shows 4 pages: Forecast | Portfolio | AI | About
         ↓
User picks a page and enters stock ticker
         ↓
App fetches live data from Yahoo Finance (yfinance API)
         ↓
Processes data through the selected module
         ↓
Shows results with interactive Plotly charts
```

---

## MODULE 1: Stock Forecast (SARIMAX)

### Step-by-Step with AAPL

```
1. User enters: AAPL, Start: Jan 2024, End: Today
2. yfinance downloads ~300 days of AAPL closing prices
3. App shows raw data table and price chart
4. Stability Check (ADF Test):
   - p-value = 0.82 > 0.05 → NOT stable ❌
   - That's OK! The 'd' parameter handles this by differencing
5. Decomposition: Splits price into Trend + Seasonal + Noise
6. User sets parameters (default p=2, d=1, q=2, S=12)
7. Click "Run Forecast"
8. SARIMAX model trains on all data
9. Predicts next 10 days of prices
10. Shows accuracy metrics:
    - RMSE = $2.50 (average error in dollars)
    - MAPE = 1.5% (average error as percentage)
    - Accuracy = 98.5% (but this is on TRAINING data!)
11. Backtest (honest check):
    - Hide last 30 days
    - Train on first 270 days
    - Predict 30 days → Compare with actual
    - Real-World Accuracy = 92% (more honest number)
```

---

## MODULE 2: Portfolio Analysis

### Step-by-Step with Default Stocks

```
Default: RELIANCE.NS, TCS.NS, HDFCBANK.NS, INFY.NS, ICICIBANK.NS, ITC.NS
Date: Jan 2021 to Jan 2024

1. Fetch 3 years of closing prices for all 6 stocks
2. Calculate daily returns for each stock
3. Show Correlation Matrix:
   - HDFCBANK & ICICIBANK: 0.75 (high → they move together, both banks)
   - TCS & ITC: 0.15 (low → good for diversification)
4. Fetch NIFTY 50 benchmark → Compare performance
5. Portfolio Optimization:
   - Generate 1000 random portfolio weight combinations
   - Calculate Return & Risk for each
   - Find:
     🏆 Best Returns: RELIANCE 35%, INFY 25%, TCS 20%, ITC 10%, ...
        Return: 22%, Risk: 18%, Sharpe: 1.1
     🛡️ Safest: ITC 30%, HDFCBANK 25%, TCS 20%, ...
        Return: 14%, Risk: 11%, Sharpe: 0.9
6. Plot Efficient Frontier (the curve of best portfolios)
7. Risk Analysis:
   - Beta = 1.15 (portfolio moves 15% more than market)
   - Max Drawdown = -18% (worst historical loss)
8. Stress Test:
   - If market crashes -20% → Your portfolio drops ~23% (Beta × -20%)
```

---

## MODULE 3: Advanced AI

### Step-by-Step with AAPL

```
User enters: AAPL → Click "Analyze Stock"

━━━ SECTION 1: News Sentiment ━━━
1. FinBERT downloads from HuggingFace (first time only, ~400MB)
2. Fetch latest AAPL news headlines from Yahoo Finance
3. Each headline → FinBERT → Score (-1 to +1)
   "Apple reports record Q4 earnings" → +0.87 (Positive)
   "iPhone sales decline in China"    → -0.65 (Negative)
   "Apple announces new MacBook"      → +0.12 (Neutral)
4. Average Score = +0.11 → Overall: Neutral

━━━ SECTION 2: Buy/Sell Signal ━━━
1. Download 2 years of AAPL prices
2. Calculate: RSI, SMA_20, SMA_50, Daily Returns
3. Label: Did price go UP next day? (1=yes, 0=no)
4. Train Random Forest (80% train, 20% test)
5. Test Accuracy = 54% (slightly better than coin flip)
6. Today's prediction: Bullish (Buy) with 62% confidence
7. Show Feature Importance chart

━━━ SECTION 3: MLP Price Forecast ━━━
1. Take all AAPL prices, scale to 0-1
2. Create sequences: [60 days] → [next day price]
3. Train MLP (90% train, 10% test)
4. R² Score = 0.85 on test set
5. Predict next 30 days

━━━ SECTION 4: LSTM Price Forecast ━━━
1. Same data preparation as MLP
2. Reshape for LSTM: (samples, 60 timesteps, 1 feature)
3. Train LSTM with early stopping
4. R² Score = 0.91 on test set (better than MLP!)
5. Predict next 30 days

━━━ SECTION 5: Model Comparison ━━━
1. Plot both forecasts on same chart
2. Comparison table:
   MLP:  R²=0.85, RMSE=$5.20, MAE=$4.10
   LSTM: R²=0.91, RMSE=$3.10, MAE=$2.50
3. Winner: LSTM ✅ (captures time patterns better)
```

---

# PART 3: ALL FORMULAS — Quick Reference

| Formula | Equation | Simple Meaning |
|---------|----------|----------------|
| **RMSE** | √(Σ(actual-pred)²/n) | Average error in same units as price |
| **MAPE** | Σ(\|actual-pred\|/actual)/n × 100 | Average error as percentage |
| **R² Score** | 1 - SS_res/SS_tot | 1 = perfect, 0 = random guess |
| **Sharpe** | (Return - FD Rate) / Risk | Return per unit of risk taken |
| **Beta** | Cov(Portfolio, Market) / Var(Market) | How much you move vs market |
| **RSI** | 100 - 100/(1 + avg_gain/avg_loss) | > 70 = overbought, < 30 = oversold |
| **SMA** | Sum(last N prices) / N | Smoothed average price |
| **Volatility** | Standard Deviation of returns | How wildly prices swing |
| **Portfolio Return** | Σ(weight × return) | Weighted average of stock returns |
| **Max Drawdown** | (Peak - Trough) / Peak | Worst loss from highest point |
| **Neuron** | activation(Σ(w×x) + b) | Weighted sum + bias + activation |
| **MSE Loss** | Σ(actual - predicted)² / n | How wrong the model is |

---

# PART 4: EXAM PANEL Q&A

### About the Project

**Q: What is your project about?**
> StockAI is an AI-powered stock market analysis platform. It has 3 modules: (1) Stock forecasting using SARIMAX time-series model, (2) Portfolio optimization using Modern Portfolio Theory, and (3) Advanced AI predictions using Neural Networks, Deep Learning, and NLP.

**Q: What problem does it solve?**
> Retail investors don't have access to expensive financial tools. Our app provides free stock analysis, price predictions, and portfolio optimization using AI — all through a simple web interface.

**Q: What is your tech stack?**
> Frontend: Streamlit. Data: Yahoo Finance API. ML: Scikit-Learn (MLP, Random Forest, GradientBoosting). Deep Learning: TensorFlow/Keras (LSTM). NLP: HuggingFace FinBERT. Optimization: SciPy. Charts: Plotly. Backend: Python with Pandas/NumPy.

---

### About AI Models

**Q: What ML algorithms does your project use?**
> Six algorithms: MLP Neural Network, LSTM Deep Learning, Random Forest Classifier, GradientBoosting Regressor, FinBERT Transformer for NLP, and SARIMAX for statistical forecasting.

**Q: Explain MLP in simple terms.**
> MLP (Multi-Layer Perceptron) is the simplest neural network. It has input neurons, hidden neurons, and output neurons. Each neuron takes inputs, multiplies by learned weights, adds a bias, and passes through an activation function (ReLU). In our app, it takes 60 past prices as input, passes through 2 hidden layers (50 and 25 neurons), and outputs 1 predicted price.

**Q: Why LSTM instead of MLP?**
> MLP sees all 60 input prices at once without understanding their order. LSTM processes them one by one, sequentially, and has memory gates that decide what past information to keep and what to forget. This makes LSTM better at capturing time-based patterns like "price has been rising for 5 days."

**Q: What are the gates in LSTM?**
> Three gates: (1) **Forget gate** — decides which old info to discard. (2) **Input gate** — decides which new info to store. (3) **Output gate** — decides what to output based on current memory. Each gate uses a sigmoid function that outputs 0 (close gate) to 1 (open gate).

**Q: What is FinBERT?**
> FinBERT is a BERT model fine-tuned on 50,000+ financial texts. BERT is a Transformer that reads text bidirectionally (both left-to-right and right-to-left) and uses "attention" to focus on important words. FinBERT understands financial terms like "bullish", "bearish", "rally" better than general NLP tools.

**Q: What is a Transformer?**
> A deep learning architecture that uses "self-attention" — instead of reading text sequentially like LSTM, it looks at ALL words simultaneously and calculates how much each word relates to every other word. This makes it faster and better at understanding context. GPT, BERT, and FinBERT are all Transformers.

**Q: What is Random Forest?**
> An ensemble of 100 decision trees. Each tree learns slightly different patterns because each sees a random subset of data. For prediction, all 100 trees vote, and we take the majority result. This "wisdom of the crowd" approach reduces errors compared to a single tree.

**Q: What is GradientBoosting?**
> An ensemble method where trees are built ONE BY ONE. Each new tree is trained to fix the mistakes of all previous trees. It's like a student who keeps doing corrections — each iteration improves accuracy. We use it with temporal features (lagged prices, rolling averages) as a fallback when LSTM/TensorFlow is unavailable.

---

### About Overfitting & Validation

**Q: How do you prevent overfitting?**
> Five techniques: (1) **Early Stopping** — stop training when validation loss increases. (2) **Dropout (0.2)** — randomly disable 20% of LSTM neurons each step. (3) **L2 Regularization** — penalize large weights in MLP. (4) **Train/Test Split** — always evaluate on unseen data. (5) **max_depth & min_samples** — limit tree complexity in Random Forest.

**Q: How do you validate your model?**
> Two ways: (1) **Train/Test Split** — 90% training, 10% testing. Metrics calculated on the 10% the model never saw. (2) **Backtesting** — hide the last 30 days of real data, train on everything before, predict those 30 days, and compare with actual prices. This gives the most honest accuracy.

**Q: What is R² Score?**
> R² measures how much of the data's variability the model explains. R²=1.0 means perfect prediction. R²=0 means the model is no better than just predicting the average price every day. R²<0 means worse than average. Our LSTM typically achieves R²=0.85-0.95.

---

### About Portfolio Theory

**Q: What is Modern Portfolio Theory?**
> MPT (Harry Markowitz, Nobel Prize 1990) says that investors should look at BOTH risk and return together, not just return alone. By combining stocks that don't move together (low correlation), you can reduce risk without sacrificing returns. The math finds the optimal weight for each stock.

**Q: What is the Efficient Frontier?**
> A curve showing the best possible portfolios. For any given risk level, the point on the curve gives the maximum possible return. We generate it by simulating 1000+ random portfolios and finding the upper boundary.

**Q: What is Sharpe Ratio?**
> It answers: "For each unit of risk I take, how much EXTRA return am I getting above a risk-free option like a bank FD?" Formula: (Portfolio Return - Risk-Free Rate) / Volatility. Higher is better. Above 1.0 is considered good.

**Q: What is Beta?**
> Beta measures how sensitive your portfolio is to market movements. Beta=1 means your portfolio moves exactly like the market. Beta=1.5 means if the market goes up 10%, your portfolio goes up 15%. We calculate it using: Covariance(Portfolio, Market) / Variance(Market).

---

### About the Code Architecture

**Q: Why did you separate code into `src/`, `views/`, `config/`?**
> For clean architecture. `views/` has the UI pages (what user sees). `src/` has the core logic (AI models, data processing). `config/` has settings. This separation means we can change the UI without touching the AI code, and vice versa.

**Q: Why `views/` and not `pages/`?**
> Streamlit reserves the `pages/` folder for its built-in multi-page feature. Using `pages/` would conflict with our custom sidebar navigation. So we renamed it to `views/`.

**Q: Why does LSTM fall back to GradientBoosting?**
> TensorFlow (needed for LSTM) doesn't support all Python versions. Our code automatically detects if TensorFlow is available. If not, it uses GradientBoosting with temporal feature engineering — which captures similar sequential patterns through lagged values and rolling statistics instead of recurrent gates.
