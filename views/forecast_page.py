
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime
from datetime import date, timedelta
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from config.config import MARKET_GROUPS

def show_forecast_page():
    # Title
    st.title('Stock Price Forecasting 📈')
    st.subheader('Predict future stock prices using AI-powered time-series analysis')

    # Add an image from online resource
    st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4EBx9mg3Tzc8Xg4ayJi2wtrXGjJDNHBc8KQ&s')

    # Sidebar
    st.sidebar.header('Select the parameters from below')

    # Market selection for suggested tickers
    selected_market = st.sidebar.selectbox("Select Market for Examples", options=list(MARKET_GROUPS.keys()), index=0)
    
    # Show example tickers based on selected market
    if selected_market == "All":
        example_tickers = "AAPL, MSFT, GOOGL, RELIANCE.NS, TCS.NS"
    else:
        example_tickers = ", ".join(MARKET_GROUPS[selected_market][:3])
    
    st.sidebar.caption(f"Example {selected_market} stocks: {example_tickers}")

    start_date = st.sidebar.date_input('Start Date', date(2024, 1, 1))
    end_date = st.sidebar.date_input('End Date', date.today())

    # Get ticker symbol from user input
    ticker = st.sidebar.text_input('Enter the company ticker symbol (e.g., AAPL)', value=example_tickers.split(',')[0].strip()).strip().upper()

    # Validate ticker input
    if not ticker:
        st.sidebar.error("Please enter a ticker symbol.")
        return

    # Fetch data from inputs using yfinance library
    data = yf.download(ticker, start=start_date, end=end_date)

    # Check if data is downloaded correctly
    if data.empty:
        st.error(f"No data found for ticker symbol '{ticker}'. Please enter a valid symbol.")
        return

    # Flatten MultiIndex columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [' '.join(col).strip() for col in data.columns.values]

    # Add Date as a column to the dataframe
    if 'Date' not in data.columns:
        data.insert(0, "Date", data.index)
    data.reset_index(drop=True, inplace=True)
    st.write('Data from', start_date, 'to', end_date)
    st.write(data)

    # Plot the data
    st.header('Data Visualization')
    st.subheader('Plot of the data')
    st.write("**Note:** Select your date range on the sidebar, or zoom in on the plot and select your specific column")
    # Exclude 'Date' from the columns to plot
    plot_columns = [col for col in data.columns if col != 'Date']
    fig = px.line(data, x='Date', y=plot_columns, title='Closing price of the stock',width=1000, height=600)
    st.plotly_chart(fig)

    # add a select box to select column from data
    column = st.selectbox('Select the column to be used for forecasting', plot_columns)

    # sub-setting the data
    data_subset = data[['Date', column]].dropna()
    st.write("Selected Data")
    st.write(data_subset)

    st.header('Is the Price Data Stable?')
    st.markdown("*Checks if the stock price has a consistent pattern (needed for accurate forecasting).*")
    try:
        st.write(adfuller(data_subset[column])[1] < 0.05)
    except Exception as e:
        st.write(f"Could not perform ADF test: {e}")

    st.header('Breaking Down the Price Data')
    st.markdown("*Separating the stock price into its main components: overall direction (trend), repeating patterns (seasonality), and random noise.*")
    try:
        decomposition = seasonal_decompose(data_subset[column], model='additive', period=12)
        st.write(decomposition.plot())
        
        # make same plot in plotly
        st.write('## Plotting the decomposition in plotly')
        st.plotly_chart(px.line(x=data_subset["Date"], y=decomposition.trend, title='Trend', width=1200, height=400, labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='Blue'))
        st.plotly_chart(px.line(x=data_subset["Date"], y=decomposition.seasonal, title='Seasonality', width=1200, height=400, labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='green'))
        st.plotly_chart(px.line(x=data_subset["Date"], y=decomposition.resid, title='Residuals', width=1200, height=400, labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='Red', line_dash='dot'))
    except Exception as e:
        st.write(f"Could not decompose data. Ensure sufficient data points. Error: {e}")

    # Let's run the model
    #  user input for three parameters of the model and seasonal order
    st.subheader('Forecasting Settings')
    st.markdown("*Adjust these to fine-tune the prediction model. Default values work well for most stocks.*")
    col_nonseasonal, col_seasonal = st.columns(2)
    
    with col_nonseasonal:
        st.markdown('**Non-Seasonal (p, d, q)**')
        p = st.slider('Select the value of p', 0, 5, 2)
        d = st.slider('Select the value of d', 0, 5, 1)
        q = st.slider('Select the value of q', 0, 5, 2)
    
    with col_seasonal:
        st.markdown('**Seasonal (P, D, Q, S)**')
        sp = st.slider('Select the value of Seasonal P', 0, 5, 1)
        sd = st.slider('Select the value of Seasonal D', 0, 5, 1)
        sq = st.slider('Select the value of Seasonal Q', 0, 5, 1)
        seasonal_period = st.number_input('Select the seasonal period (S)', 0, 24, 12)

    # Input outside button
    forecast_period = st.number_input('## Enter forecast period in days', 1, 365, 10, key="forecast_period_input")

    if st.button("Run Forecast"):
        try:
            # Create and fit the model
            model = sm.tsa.statespace.SARIMAX(data_subset[column],
                                            order=(p, d, q),
                                            seasonal_order=(sp, sd, sq, seasonal_period))
            model = model.fit()

            # predict the future values
            predictions = model.get_prediction(start=len(data_subset), end=len(data_subset)+forecast_period)
            predictions_df = predictions.predicted_mean
            
            # --- CALCULATE ACCURACY (In-Sample) ---
            fitted_values = model.fittedvalues
            actual_values = data_subset[column]
            
            rmse = np.sqrt(mean_squared_error(actual_values, fitted_values))
            
            with np.errstate(divide='ignore', invalid='ignore'):
                 mape = np.mean(np.abs((actual_values - fitted_values) / actual_values)) * 100
                 
            simple_accuracy = max(0, 100 - mape)
            
            metrics = {
                'rmse': rmse,
                'mape': mape,
                'accuracy': simple_accuracy
            }
            # --------------------------------------

            # add index to the predictions
            predictions_df.index = pd.date_range(start=end_date, periods=len(predictions_df), freq='D')
            predictions_df = pd.DataFrame(predictions_df)
            predictions_df.insert(0, 'Date', predictions_df.index, True)
            predictions_df.reset_index(drop=True, inplace=True)
            
            # Save Fitted Values for plotting
            fitted_series = fitted_values
            
            # Store results in session state
            st.session_state['forecast_results'] = {
                'model_summary': model.summary(),
                'predictions': predictions_df,
                'data_subset': data_subset,
                'column': column,
                'metrics': metrics,
                'fitted_values': fitted_series, # Saved for visualization
                'order': (p, d, q), # Save params for backtest
                'seasonal_order': (sp, sd, sq, seasonal_period)
            }
            
        except Exception as e:
            st.error(f"Error in forecasting: {e}")
            import traceback
            st.text(traceback.format_exc())

    # Check if results exist in session state
    if 'forecast_results' in st.session_state:
        results = st.session_state['forecast_results']
        predictions = results['predictions']
        data_subset = results['data_subset']
        column = results['column']

        # print model summary
        st.header('Model Summary')
        st.write(results['model_summary'])
        
        # --- Model Performance Section ---
        if 'metrics' in results:
             m = results['metrics']
             st.subheader("How Good is This Forecast?")
             
             col_main, col_detail = st.columns([2, 1])
             
             with col_main:
                 st.metric("How Well It Fits Past Data", f"{m['accuracy']:.2f}%", 
                           help="Higher = the model learned the past patterns better")
             
             with col_detail:
                 st.caption(f"Average Error (RMSE): {m['rmse']:.2f}")
                 st.caption(f"Percentage Error (MAPE): {m['mape']:.2f}%")
                 
             if m['accuracy'] > 95:
                 st.info("ℹ️ **Note**: High historical fit. See 'Backtest' below for realistic future accuracy.")
        # -----------------------------------
        
        st.write('---')

        st.write("<p style='color:green; font-size: 50px; font-weight: bold;'>Forecasting the data</p>", unsafe_allow_html=True)
        st.write('Predictions (Future)', predictions)
        # st.write('Actual Data', data_subset) # Redundant printing of full df
        
        # --- Plotting ---
        fig = go.Figure()
        
        # 1. Actual Data (Blue)
        fig.add_trace(go.Scatter(x=data_subset['Date'], y=data_subset[column],
                                 mode='lines', name='Actual History', 
                                 line=dict(color='blue')))
        
        # 2. Fitted Values (Green - Dotted) - NEW!
        if 'fitted_values' in results:
            fitted = results['fitted_values']
            # Align indices
            fig.add_trace(go.Scatter(x=data_subset['Date'], y=fitted,
                                     mode='lines', name='Model Fit (History)', 
                                     line=dict(color='green', dash='dot', width=1), opacity=0.7))
        
        # 3. Future Predictions (Red)
        fig.add_trace(go.Scatter(x=predictions['Date'], y=predictions["predicted_mean"],
                                 mode='lines', name='Future Forecast', 
                                 line=dict(color='red', width=3)))
        
        fig.update_layout(title='Actual vs Model Fit vs Forecast', xaxis_title='Date', yaxis_title='Price', width=1200, height=500)
        st.plotly_chart(fig)
        
        # --- Backtesting Section (NEW) ---
        st.write("---")
        st.header("Real-World Accuracy Check (Backtesting)")
        st.markdown("*To honestly test the model, we 'hide' the last 30 days and see if it can predict them correctly.*")
        
        if st.checkbox("Run Backtest Simulation"):
            with st.spinner("Running Backtest (Train on Past, Test on Recent)..."):
                try:
                    # 1. Split Data
                    cutoff = len(data_subset) - 30
                    train = data_subset[column].iloc[:cutoff]
                    test = data_subset[column].iloc[cutoff:]
                    
                    # 2. Train Model on Training Set ONLY
                    # Retrieve params from session
                    order = results['order']
                    seasonal_order = results['seasonal_order']
                    
                    bt_model = sm.tsa.statespace.SARIMAX(train, order=order, seasonal_order=seasonal_order)
                    bt_fit = bt_model.fit(disp=False)
                    
                    # 3. Forecast the Test Set duration
                    bt_pred = bt_fit.forecast(steps=len(test))
                    
                    # 4. Calculate Metrics on Test Set
                    bt_rmse = np.sqrt(mean_squared_error(test, bt_pred))
                    bt_mape = mean_absolute_percentage_error(test, bt_pred) * 100
                    bt_acc = max(0, 100 - bt_mape)
                    
                    # 5. Display
                    col_bt1, col_bt2 = st.columns(2)
                    with col_bt1:
                        st.metric("Real-World Accuracy", f"{bt_acc:.2f}%", 
                                  help="This is the TRUE accuracy — tested on data the model never saw during training.")
                        if bt_acc < m['accuracy']:
                             st.caption("Lower than historical fit, as expected for real predictions.")
                    with col_bt2:
                        st.metric("Test Error (RMSE)", f"{bt_rmse:.2f}")
                        
                    # Plot Backtest
                    fig_bt = go.Figure()
                    # Actual Test Data
                    fig_bt.add_trace(go.Scatter(x=data_subset['Date'].iloc[cutoff:], y=test, 
                                                mode='lines', name='Actual Price (Hidden)', line=dict(color='blue')))
                    # Predicted Test Data
                    fig_bt.add_trace(go.Scatter(x=data_subset['Date'].iloc[cutoff:], y=bt_pred, 
                                                mode='lines', name='Backtest Prediction', line=dict(color='orange', dash='dash')))
                    fig_bt.update_layout(title="Backtest: Could we predict the last 30 days?", height=400)
                    st.plotly_chart(fig_bt)
                    
                except Exception as e:
                    st.error(f"Backtest failed: {e}")

    st.write("---")
    st.markdown("<h1 style='color: green;'>Thank you for using this app!😄</h1>", unsafe_allow_html=True)
