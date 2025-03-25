# Import libraries
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import datetime
from datetime import date, timedelta
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

# Title
app_name = 'Stock Market Forecasting App'
st.title(app_name)
st.subheader('This app is created to forecast the stock market price of the entered company.')  # Updated text

# Add an image from online resource
st.image('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ4EBx9mg3Tzc8Xg4ayJi2wtrXGjJDNHBc8KQ&s')

# Take input from the user of app about the start and end date

# Sidebar
st.sidebar.header('Select the parameters from below')

start_date = st.sidebar.date_input('Start Date', date(2024, 1, 1))
end_date = st.sidebar.date_input('End Date', date(2025, 3, 16))

# Get ticker symbol from user input
ticker = st.sidebar.text_input('Enter the company ticker symbol (e.g., AAPL)').strip().upper()  # New text input

# Validate ticker input
if not ticker:
    st.sidebar.error("Please enter a ticker symbol.")
    st.stop()

# Fetch data from inputs using yfinance library
data = yf.download(ticker, start=start_date, end=end_date)

# Check if data is downloaded correctly
if data.empty:
    st.error(f"No data found for ticker symbol '{ticker}'. Please enter a valid symbol.")
    st.stop()

# Rest of your code remains the same...
# [No changes needed beyond this point except the removed ticker_list]
# Flatten MultiIndex columns if present
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [' '.join(col).strip() for col in data.columns.values]

# Add Date as a column to the dataframe
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
column = st.selectbox('Select the colomn to be used for forecasting', plot_columns)

# sub-setting the data
data = data[['Date', column]]
st.write("Selected Data")
st.write(data)

# ADF test check stationarity
st.header('Is data stationary?')
st.write(adfuller(data[column])[1] < 0.05)

# lets decompose the data
st.header('Decomposition of the data')
decomposition = seasonal_decompose(data[column], model='additive', period=12)
st.write(decomposition.plot())

# make same plot in plotly
st.write('## Plotting the decomposition in plotly')
st.plotly_chart(px.line(x=data["Date"], y=decomposition.trend, title='Trend', width=1200, height=400, labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='Blue'))
st.plotly_chart(px.line(x=data["Date"], y=decomposition.seasonal, title='Seasonality', width=1200, height=400, labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='green'))
st.plotly_chart(px.line(x=data["Date"], y=decomposition.resid, title='Residuals', width=1200, height=400, labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='Red', line_dash='dot'))

# Let's run the model
#  user input for three parameters of the model and seasonal order
p = st.slider('select the value of p', 0, 5, 2)
d = st.slider('Select the value of d', 0, 5, 1)
q = st.slider('select the value of q', 0, 5, 2)
seasonal_order = st.number_input('Select the value of seasonal p', 0, 24 , 12)

# Create and fit the model
model = sm.tsa.statespace.SARIMAX(data[column],
                                order=(p, d, q),
                                seasonal_order=(p, d, q, seasonal_order))
model = model.fit()

# print model summary
st.header('Model Summary')
st.write(model.summary())
st.write('---')

# predict the future values (Forecasting)
st.write("<p style='color:green; font-size: 50px; font-weight: bold;'>Forecasting the data</p>", unsafe_allow_html=True)

forecast_period = st.number_input('## Enter forecast period in days', 1, 365, 10)
# predict the future values
predictions = model.get_prediction(start=len(data), end=len(data)+forecast_period)
predictions = predictions.predicted_mean

# add index to the predictions
predictions.index = pd.date_range(start=end_date, periods=len(predictions), freq='D')
predictions = pd.DataFrame(predictions)
predictions.insert(0, 'Date', predictions.index, True)
predictions.reset_index(drop=True, inplace=True)
st.write('Predictions',predictions)
st.write('Actual Data', data)
st.write("---")

# let's plot the data
fig = go.Figure()
# add actual data to the plot
fig.add_trace(go.Scatter(x=data['Date'], y=data[column],mode='lines', name='Actual', line=dict(color='blue')))
# add predicted data to the plot
fig.add_trace(go.Scatter(x=predictions['Date'], y=predictions["predicted_mean"],mode='lines', name='Predicted', line=dict(color='red')))
# set the title and axis labels
fig.update_layout(title='Actual vs Predicted', xaxis_title='Date', yaxis_title='Price', width=1200, height=400)
# display the plot
st.plotly_chart(fig)

# Add buttons to show and hide separate plots
show_plots = False
if st.button('Show Separate Plots'):
    if not show_plots:
        st.write(px.line(x=data["Date"], y=data[column], title='Actual', width=1200, height=400,
                         labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='Blue'))
        st.write(
            px.line(x=predictions["Date"], y=predictions["predicted_mean"], title='Predicted', width=1200, height=400,
                    labels={'x': 'Date', 'y': 'price'}).update_traces(line_color='green'))
        show_plots = True
    else:
        show_plots = False

# add hide plots button
hide_plots = False
if st.button('Hide Separate Plots'):
    if not hide_plots:
        hide_plots = True
    else:
        hide_plots = False

st.write("---")
st.markdown("<h1 style='color: green;'>Thank you for using this app!😄</h2>", unsafe_allow_html=True)
st.write("---")
st.write("### About the author:")

st.write("<p style='color:blue; font-weight: bold ; font-size: 25px; '>- Digant Kathiriya <br>- Aryan Kanada</p>", unsafe_allow_html=True)



# st.write("## Connect with me on social media")
# # add links to my social media
# # urls of the images
# linkedin_url = "https://img.icons8.com/color/48/000000/linkedin.png"
# github_url = "https://img.icons8.com/fluent/48/000000/github.png"
#
# # redirect urls
# linkedin_redirect_url = "https://www.linkedin.com/in/digantkathiriya/"
# github_redirect_url = "https://github.com/digantk31/"
#
# # add links to the images
# st.markdown(f'<a href="{github_redirect_url}"><img src="{github_url}" width="60" height="60"></a>'
#             f'<a href="{linkedin_redirect_url}"><img src="{linkedin_url}" width="60" height="60"></a>', unsafe_allow_html=True)
