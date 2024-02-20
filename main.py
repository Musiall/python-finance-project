import streamlit as st
from pandas_datareader import data as pdr
import plotly.graph_objs as go 
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import yfinance as yfin
import plotly.express as px

yfin.pdr_override()


start = dt.datetime(2021,1,1).date() #ustawienie startu pobierania danych

# @st.cache
def get_data(ticker, start): #pobieranie danych giełdowych
    if not ticker:
        ticker = 'AAPL'
    data = pdr.get_data_yahoo(ticker, start)
    st.dataframe(data.iloc[::-1])
    return data

name = st.text_input("Insert company ticker")
data = get_data(name,start)

data = data.reset_index()

option = st.selectbox(
     'Choose Chart',
     ('Price', 'MACD', 'Stochastic Oscillator', 'Volatility'))

#plotVolatility dane
data['Log returns'] = np.log(data['Close']/data['Close'].shift())
volatility = data['Log returns'].std() * 252 ** .5 #obliczenie Volatility
str_vol = str(round(volatility, 4)*100) #\

#plotMACD dane
exp1 = data['Close'].ewm(span=12, adjust=False).mean() #exp srednia kroczaca 12dniowa 
exp2 = data['Close'].ewm(span=26, adjust=False).mean() #exp srednia kroczaca 26dniowa
data['MACD'] = exp1 - exp2 #Stworzenie kolumny 'MACD'
data['Signal Line'] = data['MACD'].ewm(span=9, adjust=False).mean() #Stworzenie kolumny 'Signal Line'

#plotOscilator dane
high14 = data['High'].rolling(14).max()
low14 = data['Low'].rolling(14).min()
data['%K'] = (data['Close'] - low14) * 100/(high14 - low14)
data['%D'] = data['%K'].rolling(3).mean()

def plotClose(data):
    fig = px.line(data,
            y='Close',  
            title="Stock Market Performance for the Last 3 Months")
    st.plotly_chart(fig)


def plotMACD(data):
    plot_data = [
        go.Scatter(
            x=data['Date'],
            y=data['MACD'],
            name = 'MACD'
        ),
        go.Scatter(
            x=data['Date'],
            y=data['Signal Line'],
            name = 'Signal Line'
        )
    ]

    plot_layout = go.Layout(
        xaxis=dict(
            type="date",  # Ensure that the type is set to 'date' for datetime x-axis
            tickformat='%b %Y',  # Sets the tick format to abbreviated month and full year
        ),
        title='MACD'
    )
    fig = go.Figure(data=plot_data, layout=plot_layout)
#pyoff.iplot(fig)
    st.pyplot(fig)
    
def plotOscilator(data):   
    fig,  ax = plt.subplots()
    data[['%K', '%D']].plot(ax=ax)
    ax.set_title(name)
    ax.axhline(80, c='r', alpha=0.3)
    ax.axhline(20, c='r', alpha=0.3)
    data['Close'].plot(ax=ax, alpha = 0.3, secondary_y = True)
    st.pyplot(fig)
    
def plotVolatility(data):
    fig, ax = plt.subplots()
    data['Log returns'].hist(ax=ax, bins = 50, alpha = 0.6, color = 'b')
    ax.set_xlabel('Log return')
    ax.set_ylabel('Freq of log returns')
    ax.set_title(name + ' Volatility: ' + str_vol + '%')
    st.pyplot(fig)

if option == 'Price':
    plotClose(data)
elif option == 'MACD':
    plotMACD(data)
elif option == 'Stochastic Oscillator':
    plotOscilator(data)
elif option == 'Volatility':
    plotVolatility(data)
    


