import streamlit as st
import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math

# Read in the data
stocks = pd.read_csv("sp_500_stocks.csv")

# Import your API token
from mysecrets import IEX_CLOUD_API_TOKEN

# Define the columns for your dataframe
my_columns = ['Ticker', 'Price','Market Capitalization', 'Number Of Shares to Buy']
final_dataframe = pd.DataFrame(columns = my_columns)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={symbol_string}&types=quote&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()

    for symbol in symbol_string.split(','):
        try:
            new_row = pd.DataFrame([[
                symbol, 
                data[symbol]['quote']['latestPrice'],
                data[symbol]['quote']['marketCap'], 
                'N/A'
            ]], 
            columns=my_columns)
            final_dataframe = pd.concat([final_dataframe, new_row], ignore_index=True)
        except KeyError:
            print(f"Data for {symbol} could not be found.")

# Streamlit code
st.title('Equal-Weight S&P 500 Index Fund')
st.write(final_dataframe)

portfolio_size = st.number_input('Enter the value of your portfolio:')

if st.button('Calculate Number of Shares to Buy'):
    position_size = float(portfolio_size) / len(final_dataframe.index)
    for i in range(0, len(final_dataframe['Ticker'])-1):
        final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
    st.write(final_dataframe)