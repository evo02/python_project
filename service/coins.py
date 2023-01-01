import pandas as pd
import numpy as np

class Coins:
    
    RSI_periods = 14 # Период для расчет RSI
    RSI_ema = True # Используем экспоненциальное
    high_RSI = 70
    low_RSI = 30
    crypto_list = ['BTC', 'ETH', 'BNB', 'XRP', 'DOGE', 'ADA', 'MATIC', 'DAI', 'DOT', 'LTC']
    prediction_interval = 5 # Дней

    def __init__(self):
        self.curr_symbol = None
        self.curr_df = None
        self.tech_info = pd.read_csv("./data/list_of_names.csv",
                            index_col=0)
        self.data = { self.crypto_list[i]:
                        pd.read_csv("./data/"+ self.crypto_list[i] + ".csv", 
                        parse_dates=["timeOpen", "timestamp"], 
                        index_col=0)
                    for i in range(len(self.crypto_list))}
        self.__preprocess()

    def _RSI(self, df, periods = 14, ema = True):
        close_delta = df['close'].diff().dropna()
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)
        if ema == True:
            ma_up = up.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
            ma_down = down.ewm(com = periods - 1, adjust=True, min_periods = periods).mean()
        else:   
            ma_up = up.rolling(window = periods, adjust=False).mean()
            ma_down = down.rolling(window = periods, adjust=False).mean()
        rsi = ma_up / ma_down
        rsi = 100 - (100/(1 + rsi))
        return rsi

    def __preprocess(self):
        for i, j in self.data.items():
            temp_name = self.data[i]
            temp_data = j
            temp_data.reset_index(drop=True, inplace=True)
            temp_data.drop(columns='timestamp', inplace=True)
            temp_data["close_rsi"] = self._RSI(df=temp_data, periods=self.RSI_periods, ema=self.RSI_ema)
            temp_data["high_rsi"] = self.high_RSI
            temp_data["low_rsi"] = self.low_RSI
            temp_data.dropna(inplace=True)
            temp_data.set_index('timeOpen', inplace=True)
    
    def pick_coin(self, coin_symbol):
        self.curr_symbol = coin_symbol
        self.curr_df = self.data[coin_symbol]
    
    def update_data(self):
        self.data = { self.crypto_list[i]:
                        pd.read_csv("./data/"+ self.crypto_list[i] + ".csv", 
                        parse_dates=["timeOpen", "timestamp"], 
                        index_col=0)
                    for i in range(len(self.crypto_list))}
        self.__preprocess()
