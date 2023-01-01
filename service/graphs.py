import plotly.graph_objs as go
import streamlit as st
import plotly.express as px
import datetime
import pandas as pd
import numpy as np

from plotly.subplots import make_subplots
from pandas import DataFrame
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import VotingRegressor
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split

def get_candlestick_graph(df: DataFrame):
    df['MA5'] = df['close'].rolling(5).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['open'],
                                 high=df['high'],
                                 low=df['low'],
                                 close=df['close'], 
                                 name='Price'), 
                                 row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, 
                             y=df['MA20'], 
                             line=dict(color='blue', width=1.5), 
                             name='Long Term MA'),
                             row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, 
                             y=df['MA5'], 
                             line=dict(color='orange', width=1.5), 
                             name='Short Term MA'),
                             row=1, col=1)
    fig.add_trace(go.Bar(x=df.index ,
                         y=df["volume"],
                         marker_color='#1f77b4',
                         name='Volume'),
                         row=2, col=1)
    fig.update_layout(title="Свечной график",
                      xaxis_title="Date",
                      )
    fig.update_xaxes(rangeslider= {'visible':False}, tickmode = 'array', row=1, col=1)
    fig.update_xaxes(matches='x')
    fig.update_xaxes(rangeslider= {'visible':True}, tickmode = 'array', row=2, col=1)
    fig.update_layout(
        xaxis=dict(rangeselector=dict(
            buttons=list([
                dict(count=7, label="Last Week", step="day", stepmode="backward"),
                dict(count=1, label="Last Month", step="month", stepmode="backward"),
                dict(count=6, label="Last 6 Months", step="month", stepmode="backward"),
                dict(count=1, label="Last Year", step="year", stepmode="backward"),
                dict(step="all")
            ]))
        )
    )
    fig.update_layout(height=800)
    return fig

def get_rsi_graph(df: DataFrame):
    fig2 = make_subplots(rows=2, cols=1)
    fig2.add_trace(go.Scatter(x=df.index, 
                                y=df['close'],
                                mode='lines',
                                name='close',
                                showlegend =False,
                                line=dict(color="#d62728", width=4)),
                    row=1, 
                    col=1)
    fig2.add_trace(go.Scatter(x=df.index,
                                y=df['low'],
                                fill='tonexty',
                                mode='lines',
                                name='low',
                                showlegend =False,                   
                                line=dict(width=2, color='pink', dash='dash')),
                    row=1, 
                    col=1)
    fig2.add_trace(go.Scatter(x=df.index, 
                                y=df['high'],
                                fill='tonexty',
                                mode='lines',
                                name='high',
                                showlegend =False, 
                                line=dict(width=2, color='pink', dash='dash')),
                    row=1, 
                    col=1)
    fig2.add_trace(go.Scatter(x=df.index, y=df['close_rsi'],
                                mode='lines',
                                name='RSI',
                                line=dict(color="#1f77b4", width=1)),
                    row=2, 
                    col=1)
    fig2.add_trace(go.Scatter(x=df.index,
                                y=df['low_rsi'],
                                fill='tonexty', 
                                mode='lines',
                                name='low RSI',
                                showlegend =False,                   
                                line=dict(width=2, color='aquamarine', dash='dash')),
                    row=2, 
                    col=1)
    fig2.add_trace(go.Scatter(x=df.index, 
                                y=df['high_rsi'],
                                fill='tonexty',
                                mode='lines',
                                name='high RSI',
                                showlegend =False, 
                                line=dict(width=2, color='aquamarine', dash='dash')),
                    row=2,
                    col=1)
    fig2.update_layout(title="График с RSI",
                      xaxis_title="Date",
                      )
    fig2.update_xaxes(rangeslider= {'visible':False}, tickmode = 'array', row=1, col=1)
    fig2.update_xaxes(matches='x')
    fig2.update_xaxes(rangeslider= {'visible':True}, tickmode = 'array', row=2, col=1)

    fig2.update_layout(
        xaxis=dict(rangeselector=dict(
            buttons=list([
                dict(count=7, label="Last Week", step="day", stepmode="backward"),
                dict(count=1, label="Last Month", step="month", stepmode="backward"),
                dict(count=6, label="Last 6 Months", step="month", stepmode="backward"),
                dict(count=1, label="Last Year", step="year", stepmode="backward"),
                dict(step="all")
            ]))
        )
    )
    fig2.update_layout(height=800)
    return fig2


def _get_model(df, interval: int=7):
    tmp_df = df.drop(['open', 'high', 'low', 'volume', 'close_rsi', 'high_rsi', 'low_rsi', 'marketCap'], axis=1).copy()
    tmp_df['pred'] = tmp_df[['close']].shift(-interval)
    X = np.array(tmp_df[['close']])
    X = X[:-interval]
    y_ = tmp_df['pred'].values
    y_ = y_[:-interval]
    x_train, x_test, y_train, y_test = train_test_split(X,y_,test_size=0.15)
    model = VotingRegressor([
                         ('KNN', KNeighborsRegressor(n_neighbors=interval)),
                         ('Tree', DecisionTreeRegressor()),
                         ('Lasso', Lasso())
                         ])
    model.fit(x_train,y_train)
    model_score = model.score(x_test,y_test)
    X_proj = np.array(df[['close']])[-interval:]
    res = model.predict(X_proj)

    start_dt = df.index[-1].to_pydatetime().replace(tzinfo=None) + datetime.timedelta(days=(1))
    end_dt = start_dt + datetime.timedelta(days=(interval-1))
    index = pd.date_range(start_dt, end_dt)
    output_df = pd.DataFrame(data = res, index=index, columns=['close'])
    return output_df, model_score

def get_model(df):
    week_mod = _get_model(df, interval=7)
    fig1 = px.line(x=week_mod[0].index, y=week_mod[0].close,
                    labels={'x': 'Date', 'y': 'Close'},
                    markers=True)
    fig1.update_traces(line_color='#76D714', line_width=5)

    month_mod = _get_model(df, interval=30)
    fig2 = px.line(x=month_mod[0].index, y=month_mod[0].close,
                      labels={'x': 'Date', 'y': 'Close'},
                      markers=True)
    fig2.update_traces(line_color='#76D714', line_width=5)  # 00ff00
    return fig1, week_mod[1], fig2, month_mod[1]