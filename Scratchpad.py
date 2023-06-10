from ml_models import dataframes_from_queries
import pandas as pd
from datetime import date, timedelta, datetime
import time
from sqlalchemy import create_engine
from sec_edgar_downloader import Downloader
import psycopg2
import passwords
import requests
import json
import edgar_jobs
import yfinance as yf


# def one_time_update_stock_data():
#     symbols = []
#     for ticker in symbols_list:
#         try:
#             msft = yf.Ticker("CRM")
#             downloaded_data = yf.download(ticker, start='2023-05-26', end=date.today())
#             msft_info = msft.info['sector']
#             print("info", msft_info)
#         except (ValueError, KeyError, Exception) as error:
#             print(f"{error} for {ticker}")
#             continue
#         downloaded_data['Symbol'] = ticker
#         symbols.append(downloaded_data)
#     df = pd.concat(symbols)
#     print(df)
#     df = df.reset_index()
#     df = df[['Date', 'Open', 'Close', 'Symbol']]
#     df.columns = ['created_at', 'open_price', 'close_price', 'stock_symbol']
#     df = df.drop_duplicates()
#     print("stocks done")

# one_time_update_stock_data()



# print(data)