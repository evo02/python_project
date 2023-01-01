import streamlit as st
from streamlit_option_menu import option_menu
from service.coins import Coins
from service.get_buttons import *

st.set_page_config(
    page_title="Криптовалютный Дашборд",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto")

st.markdown("<center><h1 Style=\"overflow: visible; padding-bottom: 50px; padding-top: 0px;\">Криптовалютный Дашборд </h1></center>", unsafe_allow_html=True)

selected = option_menu(
        menu_title=None,
        options = ["Объемы", "Графики", "Stonks", "О проекте"],
        icons = ['list', 'bar-chart-fill', 'graph-up-arrow', 'info'],
        default_index = 0,
        orientation = "horizontal",
        styles={
        "container": {"padding": "5!important", "background-color": "black"},
        "icon": {"color": "#ffbf00", "font-size": "28px"},
        "nav-link": {"font-size": "28px", "text-align": "center", "margin":"0px", "--hover-color": "black"},
        "nav-link-selected": {"background-color": "#a67c00"},
}
)


coin = Coins()

if selected == "Объемы":
    get_volumes(coin)
elif selected == "Графики":
    get_main_graphs(coin)
elif selected == "Stonks":
    get_stonks(coin)
elif selected == "О проекте":
    get_stonks(coin)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
