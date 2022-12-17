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
import dataframes_from_queries
import os
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta, datetime
import time
from sqlalchemy import create_engine
from sec_edgar_downloader import Downloader
import psycopg2
import passwords
import edgar_jobs
import top_correlations

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

symbols_list = dataframes_from_queries.stock_dropdown()


# symbols_list = ['COIN', 'AAPL']

def get_dates():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    year = int(yesterdays_date[0:4])
    month = int(yesterdays_date[5:7])
    day = int(yesterdays_date[8:10])

    yesterday = str(date(year, month, day))
    return yesterday


def update_edgar_files(filing_type):
    print("starting updates", datetime.now())
    for ticker in symbols_list:
        dl = Downloader()
        try:
            dl.get(f"{filing_type}", ticker, after=f"2022-12-07", before=f"{get_dates()}")
        except Exception as error:
            print(error)
            continue
    print("ending updates", datetime.now())


def append_to_postgres(df, table, append_or_replace):
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    find_open_queries = f'''
            SELECT pid FROM pg_locks l 
            JOIN pg_class t ON l.relation = t.oid AND t.relkind = 'r' 
            WHERE t.relname = '{table}'
            '''
    pid_list = pd.read_sql(find_open_queries, con=connect)
    pid_list = pid_list.values.tolist()
    for pids in pid_list:
        for pid in pids:
            kill_open_queries = f'''
                SELECT pg_terminate_backend({pid});
                '''
            kill_list = pd.read_sql(kill_open_queries, con=connect)
            print(kill_list)
    print("query killed")
    df = df
    try:
        df.to_sql(table, con=conn, if_exists=append_or_replace,
                  index=False)
        conn = psycopg2.connect(conn_string
                                )
        conn.autocommit = True
        cursor = conn.cursor()
        conn.close()
    except Exception as e:
        print('Error: ', e)
        conn.rollback()


def update_stock_data():
    symbols = []
    for ticker in symbols_list:
        try:
            downloaded_data = data.DataReader(ticker, 'yahoo', f'{get_dates()}', f'{get_dates()}')
        except (ValueError, KeyError, Exception) as error:
            print(f"{error} for {ticker}")
            continue
        downloaded_data['Symbol'] = ticker
        symbols.append(downloaded_data)
    df = pd.concat(symbols)
    df = df.reset_index()
    df = df[['Date', 'Close', 'Symbol']]
    df.columns = ['created_at', 'close_price', 'stock_symbol']
    df.head()
    append_to_postgres(df, 'ticker_data', 'append')
    print("Stock Done")


def keyword_count_cron_job():
    keyword_list = dataframes_from_queries.keyword_list
    full_df = pd.DataFrame(columns=['keyword_mentions', 'keyword', 'total_filings', 'filing_type', 'filing_week'])
    for keywords in keyword_list:
        query_results = f'''
          with count_inflation_mentions as (
          select date(filing_date) as filing_date,
          filing_url,
          filing_type,
          case when risk_factors ilike '%%{keywords}%%' then 1
          when risk_disclosures ilike '%%{keywords}%%' then 1
          else 0
          end as inflation_count
          from public.edgar_data
          order by filing_date desc)

          select sum(inflation_count) as keyword_mentions,
          '{keywords}' as "keyword",
          count(filing_url) as total_filings,
          filing_type,
          DATE_TRUNC('week',filing_date) as filing_week
          from count_inflation_mentions
          group by filing_week, filing_type
          order by filing_week desc
            '''
        query_results_df = pd.read_sql(query_results, con=connect)
        full_df = full_df.append(query_results_df, ignore_index=True)
    print("df_ready_to_write")
    append_to_postgres(full_df, 'keyword_weekly_counts', 'append')
    print("Keywords Done")


def weekly_stock_opening_cron_job():
    print("starting query")
    query_results = f'''
        with temp_table as (
        select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol
        from public.ticker_data
        order by stock_symbol, date(created_at)  asc
        )

      SELECT
          created_at,
          close_price,
          stock_symbol,
          LAG(created_at,1) OVER (
              ORDER BY stock_symbol, created_at
          ) as next_date,
              case when LAG(created_at) OVER (
              ORDER BY stock_symbol, created_at
          ) = created_at then null else created_at
          end as first_price_in_week
      FROM
          temp_table
        '''
    query_results_df = pd.read_sql(query_results, con=connect)
    print("query done")
    append_to_postgres(query_results_df, 'weekly_stock_openings', 'replace')
    print("Stock Window Functions Done")


def top_correlation_scores():
    # grab the keywords we want to test
    keywords_dict = dataframes_from_queries.keyword_list
    # time delays to test
    time_delay_dict = ['4']
    filing_type = ['10-Q']
    # grab the first date of each week within the time bound we're interested in
    dates_dict = f'''
            with first_week_dates as (
            with temp_table as (
            select DATE_TRUNC('month',created_at) as created_at, close_price, stock_symbol
            from public.ticker_data
            order by stock_symbol, date(created_at)  asc
            )

            SELECT
              created_at,
              close_price,
              stock_symbol,
              LAG(created_at,1) OVER (
                  ORDER BY stock_symbol, created_at
              ) as next_date,
                  case when LAG(created_at) OVER (
                  ORDER BY stock_symbol, created_at
              ) = created_at then null else created_at
              end as first_price_in_week
            FROM
              temp_table
              where stock_symbol = 'CRM')

            select to_char(first_price_in_week, 'YYYY-MM-DD') as date_strings from first_week_dates
            where first_price_in_week is not null
            and first_price_in_week >= '2021-01-01'
            and first_price_in_week <= '2021-02-01'
        '''
    dates_dict = pd.read_sql(dates_dict, con=connect)
    dates_dict = dates_dict['date_strings'].tolist()

    list_of_all_correlations = []
    print("starting correlation for loop")

    for dates in dates_dict:
        for time_delays in time_delay_dict:
            for keywords in keywords_dict:
                for filings in filing_type:
                    query_results = f'''
                        with top_correlations as (with rolling_average_calculation as (
                         with keyword_data as (select * from keyword_weekly_counts where keyword = '{keywords}'),
                        stock_weekly_opening as (select * from weekly_stock_openings)

                        select 
                        distinct first_price_in_week as stock_date
                        , close_price
                        , stock_symbol
                        , 1.00 * keyword_mentions / total_filings as keyword_percentage
                        from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week + interval '{time_delays} week'
                        where first_price_in_week >= '{dates}'
                        and first_price_in_week <= '{get_dates()}'
                        and filing_type = '{filings}'
                        )

                        select stock_date, stock_symbol,
                        close_price,
                        'keyword Mentions' as keyword_mentions,
                        avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                        from rolling_average_calculation
                        order by stock_symbol, stock_date
                        )

                        select stock_symbol as "Stock Symbol", '{keywords} Mentions' as "Keyword",
                        '{dates}' as "Start Date",
                        '{get_dates()}' as "End Date",
                        {time_delays} as time_delay,
                        '{filings}' as filing_type,
                        corr(close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
                        from top_correlations
                        where stock_date >= '{dates}'
                        and stock_date <= '{get_dates()}'
                        group by 1, 2
                        order by Correlation desc
                        limit 10
                        '''
                    df_results = pd.read_sql(query_results, con=connect)
                    df_results = df_results.round({'correlation': 4})
                    list_of_all_correlations.append(df_results)

    list_of_all_correlations = pd.concat(list_of_all_correlations, ignore_index=True)
    print("finished correlation for loop")
    df = pd.DataFrame(list_of_all_correlations)
    print(df)

# top_correlation_scores()