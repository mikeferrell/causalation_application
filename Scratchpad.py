# import pandas as pd
# import passwords
# from sqlalchemy import create_engine
#
# url = passwords.rds_access
#
# engine = create_engine(url)
# connect = engine.connect()
#
# keyword_count = f'''select distinct keywords, keyword_count from public.rake_data
# order by keyword_count desc'''
# keyword_count_df = pd.read_sql(keyword_count, con=connect)
# keyword_count_df= keyword_count_df.iloc[:, 0]
# print(keyword_count_df)

# number_list = list(range(1,21,1))
#
# print(number_list)


#YAML file for ElasticBeanstalk called config.YAML
# branch-defaults:
#   default:
#     environment: null
#     group_suffix: null
#   master:
#     environment: null
#     group_suffix: null
# environment-defaults:
#   flask-env:
#     branch: null
#     repository: null
# global:
#   application_name: causalation3
#   branch: master
#   default_ec2_keyname: aws-eb
#   default_platform: Python 3.8
#   default_region: us-east-1
#   include_git_submodules: true
#   instance_profile: null
#   platform_name: null
#   platform_version: null
#   profile: null
#   repository: Causalation2
#   sc: git
#   workspace_type: Application

import dataframes_from_queries
import schedule
import pandas as pd
from pandas_datareader import data
import pandas_datareader as pdr
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
from sqlalchemy import create_engine
import psycopg2
import passwords



# today = date.today()
# yesterdays_date = today - timedelta(days=1)
# yesterdays_date = str(yesterdays_date)
# start_year = int(yesterdays_date[0:4])
# start_month = int(yesterdays_date[5:7])
# start_day = int(yesterdays_date[8:10])
#
# todays_date = str(today)
# end_year = int(todays_date[0:4])
# end_month = int(todays_date[5:7])
# end_day = int(todays_date[8:10])



# start_date = date(start_year, start_month, start_day)
# end_date = date(end_year, end_month, end_day)
# symbols_list = dataframes_from_queries.stock_dropdown()
# symbols_list = ['DDOG', 'AAPL']
# start_date = '2022-11-01'
# end_date = '2022-11-01'
#
# symbols = []
# for ticker in symbols_list:
#     try:
#         downloaded_data = data.DataReader(ticker, 'yahoo', start_date, end_date)
#     except ValueError:
#         continue
#     downloaded_data['Symbol'] = ticker
#     symbols.append(downloaded_data)
# df = pd.concat(symbols)
# df = df.reset_index()
# df = df[['Date', 'Close', 'Symbol']]
# df.columns = ['created_at', 'close_price', 'stock_symbol']
# df.head()
# print(df)


# from pandas_datareader import data
# from datetime import datetime, date
# from apscheduler.schedulers.background import BackgroundScheduler
# import os
# import time
# from sqlalchemy import create_engine
# import psycopg2
# import passwords
# import sandp500V2
# from sec_edgar_downloader import Downloader
# import edgar_data_to_rds as edgar_analysis


# import pathlib
#
# file_path = pathlib.PurePath(__file__).parent
# print(file_path)

