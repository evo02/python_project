import streamlit as st
import requests
import datetime
import pandas as pd 
from streamlit_lottie import st_lottie_spinner
from .graphs import get_candlestick_graph, get_rsi_graph, get_model
from .coins import Coins
from .parse import fill_parse
from pandas import DataFrame

def _actual_check(coin: Coins) -> bool:
    tmp_date_now = datetime.date.today()
    tmp = datetime.datetime(tmp_date_now.year, tmp_date_now.month, tmp_date_now.day, 0, 0)
    if coin.data['BTC'].index[-1].to_pydatetime().replace(tzinfo=None) < (tmp - datetime.timedelta(days=(1))):
        return True
    else: return False

def _actual_checker(coin: Coins) -> None:
    if _actual_check(coin)==True:
        fill_parse(coin)
        coin.update_data
        st.info('Данные только что были обновлены')

def get_volumes(coin: Coins) -> None:
    _actual_checker(coin)
    for i in range(len(coin.crypto_list)):
        coin.pick_coin(coin.crypto_list[i])
        df = coin.curr_df
        price = df['close'].iloc[-1]
        price_ch = (df['close'].iloc[-2] - df['close'].iloc[-1])/df['close'].iloc[-2]
        marketcap = df['marketCap'].iloc[-1]
        marketcap_ch = (df['marketCap'].iloc[-2] - df['marketCap'].iloc[-1])/df['marketCap'].iloc[-2]
        volume = df['volume'].iloc[-1]
        volume_ch = (df['volume'].iloc[-2] - df['volume'].iloc[-1])/df['volume'].iloc[-2]
        cl1,col1, col2, col3,col4 = st.columns([0.5,1,2,2.5,2.5])
        with cl1:
            st.write(i+1)
        with col1:
            st.image("./images/"+coin.crypto_list[i]+".png", width=75)
        with col2:
            st.metric(label=coin.crypto_list[i], value=(str(round(price, 1)))+" $", delta=str(round(price_ch, 2)) + "%")
        with col3:
            st.metric(label="Volume (24h)", value=(str(round(volume, 1)))+" $", delta=str(round(volume_ch, 2)) + "%")
        with col4:
            st.metric(label="Market Capitalization", value=(str(round(marketcap, 1)))+" $")

def _load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

_lottie_url = "https://assets3.lottiefiles.com/private_files/lf30_h4qnjuax.json"

def get_main_graphs(coin: Coins) -> None:
    _actual_checker(coin)
    with st.form(key='form'):
        crpt = st.selectbox('Выбрать валюту', coin.crypto_list)
        submit_button = st.form_submit_button(label='Отправить')
    if submit_button:
        if crpt in coin.crypto_list:
            st.info("Примечание: возможно двигать интервал даты вручную по нижнему слайдеру")
            st.info("Примечание 2: в теории пересечение короткой и длинной скользящих средних дает сигнал к покупке/продаже")
            with st_lottie_spinner(_load_lottieurl(_lottie_url)):
                coin.pick_coin(crpt)
                df = coin.curr_df.copy()
                fig1 = get_candlestick_graph(df)
                st.plotly_chart(fig1, use_container_width=True)
                fig2 = get_rsi_graph(df)
                st.plotly_chart(fig2, use_container_width=True)

def get_stonks(coin: Coins) -> None:
    _actual_checker(coin)
    st.warning("Данные результаты не гарантируют прибыль")
    with st.form(key='form'):
        crpt = st.selectbox('Выбрать валюту', coin.crypto_list)
        submit_button = st.form_submit_button(label='Отправить')
    if submit_button:
        if crpt in coin.crypto_list:
            with st_lottie_spinner(_load_lottieurl(_lottie_url)):
                coin.pick_coin(crpt)
                df = coin.curr_df.copy()
                figs = get_model(df)
                st.header("Stonks на 7 дней вперед:")
                st.write("R^2 на тестовой выборке: ", str(round(figs[1], 3)))
                figs[0].update_layout(title='Прогнозирование ' + crpt)
                st.plotly_chart(figs[0], use_container_width=True)

                st.header("Stonks на 30 дней вперед:")
                st.write("R^2 на тестовой выборке: ", str(round(figs[3], 3)))
                figs[2].update_layout(title='Прогнозирование ' + crpt)
                st.plotly_chart(figs[2], use_container_width=True)