import requests
import json
import pandas as pd
import datetime
import time
from .coins import Coins
from requests.adapters import HTTPAdapter, Retry

_retry_strategy = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[ 500, 502, 503, 504 ]
    )

_adapter = HTTPAdapter(max_retries=_retry_strategy)
_http = requests.Session()
_http.mount("https://", _adapter)
_http.mount("http://", _adapter)

def _unix_time(tmp: datetime.datetime) -> int:
    return int(time.mktime(tmp.timetuple()))

def _get_coinmarketcap_cryptocurrency(id: int, start: int, end: int):
        url = f'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id={id}&convertId=2781&timeStart={start}&timeEnd={end}'
        response = _http.get(url)
        data = []
        for item in response.json()['data']['quotes']:
            date = item['timeOpen']
            open_ = item['quote']['open']
            close = item['quote']['close']
            volume =item['quote']['volume']
            marketCap =item['quote']['marketCap']
            date2 = item['quote']['timestamp']
            high = item['quote']['high']
            low = item['quote']['low']
            data.append([date, open_, close, volume, marketCap, date2, high, low])
        return data

def coinmarketcap_info_to_csv():
    
    api_url_id = 'https://api.coinmarketcap.com/data-api/v1/cryptocurrency/map'
    response = _http.get(api_url_id)

    def get_coinmarketcap_info(url: str):
        for item in response.json()['data']:
            identificator = item['id']
            name = item['name']
            symbol = item['symbol']
            is_active = item['is_active']
            yield identificator, name, symbol, is_active
    cols = ["id", "name", "symbol", "is_active"]
    dataframe = (elem for elem in get_coinmarketcap_info(api_url_id))
    df_names = pd.DataFrame(dataframe, columns= cols)
    df_names.to_csv('./data/list_of_names.csv')


def full_parse():
    '''
    Полный сбор данных о криптовалютах

    '''
    crypto_list = ['BTC', 'ETH', 'BNB', 'XRP', 'DOGE', 'ADA', 'MATIC', 'DAI', 'DOT', 'LTC']
    df_names = pd.read_csv("./data/list_of_names.csv",index_col=0)
    final_list = df_names.loc[df_names['symbol'].isin(crypto_list)].reset_index(drop=True)

    DAYS_FROM_NOW_FOR_PARSE = 2200

    # Дата окончания - текущий день
    tmp_date_now = datetime.date.today()

    # Выявлено методом тыка, что api выдает ровно 3 часа ночи
    date_now = datetime.datetime(tmp_date_now.year, tmp_date_now.month, tmp_date_now.day, 3, 0)

    # Дата старта
    date_start = date_now - datetime.timedelta(days=DAYS_FROM_NOW_FOR_PARSE)

    unix_date_start = int(time.mktime(date_start.timetuple()))
    unix_date_now = int(time.mktime(date_now.timetuple()))

    api_url_cryptocurrency = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id=1&convertId=2781&timeStart=1420070400&timeEnd=1637712000'
    
    max_delta=99
    cols = ["timeOpen", "open", "close", "volume", "marketCap", "timestamp", "high", "low"]
    # Очень аккуратно бегаем по датам
    # Делаем запросы по времени от start до start + 99 дней или до start + n, где n - дней до текущей даты
    for i in range(len(final_list)):
        df_temp = pd.DataFrame()
        start_tmp = date_start
        while True:
            tmp_delta = max_delta
            unix_tmp_start = _unix_time(start_tmp)
            if (date_now - start_tmp).days <= 0: break 
            elif (date_now - start_tmp).days > max_delta:
                tmp = max_delta
                unix_tmp_end = _unix_time(start_tmp+datetime.timedelta(days=(tmp-1)))
                df_temp = pd.concat([df_temp, pd.DataFrame(_get_coinmarketcap_cryptocurrency(final_list.iloc[i][0], unix_tmp_start, unix_tmp_end), columns= cols)])
            else:
                tmp = (date_now - start_tmp).days
                unix_tmp_end = _unix_time(start_tmp+datetime.timedelta(days=(tmp)))
                df_temp = pd.concat([df_temp, pd.DataFrame(_get_coinmarketcap_cryptocurrency(final_list.iloc[i][0], unix_tmp_start, unix_tmp_end), columns= cols)])
            start_tmp+=datetime.timedelta(days=tmp)
            
        df_temp.reset_index(drop=True).to_csv("./data/" + final_list.iloc[i][2]+'.csv')
        print(final_list.iloc[i][1] + ' saved!')


def fill_parse(coin: Coins):
    ''' Дозаписываем файлы до текущего дня'''
    crypto_list = ['BTC', 'ETH', 'BNB', 'XRP', 'DOGE', 'ADA', 'MATIC', 'DAI', 'DOT', 'LTC']
    df_names = pd.read_csv("./data/list_of_names.csv",index_col=0)
    final_list = df_names.loc[df_names['symbol'].isin(crypto_list)].reset_index(drop=True)

    # Берем дату только BTC, т.к. парсим все монеты одинаково
    date_start = coin.data['BTC'].index[-1].to_pydatetime().replace(tzinfo=None) + datetime.timedelta(days=(1))
    tmp_date_now = datetime.date.today()
    date_now = datetime.datetime(tmp_date_now.year, tmp_date_now.month, tmp_date_now.day, 3, 0)
    max_delta=99
    cols = ["timeOpen", "open", "close", "volume", "marketCap", "timestamp", "high", "low"]
    for i in range(len(final_list)):
        df_temp = pd.DataFrame()
        start_tmp = date_start
        while True:
            tmp_delta = max_delta
            unix_tmp_start = _unix_time(start_tmp)
            if (date_now - start_tmp).days <= 0: break 
            elif (date_now - start_tmp).days > max_delta:
                tmp = max_delta
                unix_tmp_end = _unix_time(start_tmp+datetime.timedelta(days=(tmp-1)))
                df_temp = pd.concat([df_temp, pd.DataFrame(_get_coinmarketcap_cryptocurrency(final_list.iloc[i][0], unix_tmp_start, unix_tmp_end), columns= cols)])
            else:
                tmp = (date_now - start_tmp).days
                unix_tmp_end = _unix_time(start_tmp+datetime.timedelta(days=(tmp)))
                df_temp = pd.concat([df_temp, pd.DataFrame(_get_coinmarketcap_cryptocurrency(final_list.iloc[i][0], unix_tmp_start, unix_tmp_end), columns= cols)])
            start_tmp+=datetime.timedelta(days=tmp)
        df_temp.reset_index(drop=True, inplace=True)
        with open("./data/" + final_list.iloc[i][2]+'.csv', 'a') as f:
            df_temp.to_csv(f, header=False)
        f.close()
        print(final_list.iloc[i][1] + ' overwritten!')
