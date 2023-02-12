import numpy as np
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta, datetime
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sqlalchemy import create_engine
import psycopg2
import passwords

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


def format_percent(value):
    return "{:.0%}".format(value)

def format_dollar(value):
    return "${:.2f}".format(value)


def defined_dates():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    y_year = int(yesterdays_date[0:4])
    y_month = int(yesterdays_date[5:7])
    y_day = int(yesterdays_date[8:10])
    one_month_ago = today - timedelta(months=1)
    one_month_ago = str(one_month_ago)
    oma_year = int(one_month_ago[0:4])
    oma_month = int(one_month_ago[5:7])
    oma_day = int(one_month_ago[8:10])
    two_month_ago = today - timedelta(months=1)
    two_month_ago = str(two_month_ago)
    tma_year = int(two_month_ago[0:4])
    tma_month = int(two_month_ago[5:7])
    tma_day = int(two_month_ago[8:10])

    yesterday = str(date(y_year, y_month, y_day))
    one_month_ago = str(date(oma_year, oma_month, oma_day))
    two_month_ago = str(date(tma_year, tma_month, tma_day))
    return yesterday, one_month_ago, two_month_ago


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

def backtesting():
    df_for_pg_upload = pd.DataFrame(columns=[
        'stock_symbol', 'buy_week', 'buy_price', 'prediction_date', 'predicted_close_price', 'predicted_price_change'
    , 'cashout_price', 'predicted_price_change_percentage', 'keyword', 'time_delay', 'filing_type', 'start_date'
    ])

    top_correlation_query_results = f'''
    select "Stock Symbol" as stock_symbol
    , split_part("Keyword", ' Mentions', 1) as keyword
    , "Start Date" as start_date
    , "End Date" as end_date
    , time_delay
    , filing_type
    , correlation
    from public.all_correlation_scores
    where correlation is not null
      and date("Start Date") <= current_date - interval '40 week'
      and "Stock Symbol" != 'GEHC'
      and "Keyword" != 'cryptocurrency Mentions'
    order by correlation desc
    limit 10
    '''
    query_df = pd.read_sql(top_correlation_query_results, con=connect)

    row_range = range(0, 10)
    for rows in row_range:
        df_row = query_df.iloc[rows]
        stock_symbol = df_row['stock_symbol']
        keyword = df_row['keyword']
        correlation_start_date = df_row['start_date']
        interval = df_row['time_delay']
        filing_type = df_row['filing_type']

        buy_recommendation = f'''with prediction_testing as (
              with prices as (
              select stock_symbol, start_date, keyword, time_delay, filing_type, to_date(cast(current_week as text), 'YYYYMMDD') as current_week, current_close_price
              , stock_date as prediction_date, predicted_price as next_week_predicted_close, next_week_close_price
              , case when next_week_close_price > current_close_price then 'price increased'
                  when next_week_close_price < current_close_price then 'price decreased'
                  when next_week_close_price is null then 'no price comparison'
                  else 'price the same'
                  end as actual_price_movement
              , next_week_close_price - current_close_price as actual_price_change
              , (next_week_close_price / current_close_price) - 1 as actual_price_change_percentage
              , case when current_close_price < predicted_price then 'price increased'
                  when current_close_price > predicted_price then 'price decreased'
                  when predicted_price is null then 'no price comparison'
                  else 'price the same'
                  end as predicted_price_movement
              , predicted_price - current_close_price as predicted_price_change 
              , (current_close_price / predicted_price) - 1 as predicted_price_change_percentage 
              from top_five_prediction_results
              where 
              stock_symbol = '{stock_symbol}'
              and keyword = '{keyword}'
              and start_date = '{correlation_start_date}'
              and time_delay = '{interval}'
              and filing_type = '{filing_type}'
              order by current_week asc
              )
            
              SELECT
              stock_symbol, keyword, time_delay, filing_type, start_date, current_week, prediction_date, current_close_price
              , next_week_close_price  as actual_price_week_of_prediction, next_week_predicted_close as predicted_close_price
              , actual_price_change
              , predicted_price_change
              , predicted_price_change_percentage
              , case when actual_price_movement = 'no price comparison' then 'no price comparison'
                  when actual_price_movement = predicted_price_movement then 'correct prediction'
                  else 'incorrect prediction'
                  end as prediction_validation
              , actual_price_change - predicted_price_change as actual_prediction_delta
              , case when actual_price_change = 0 then null else (actual_price_change - predicted_price_change) / current_close_price end as actual_prediction_percentage_delta
              from prices
            ),
            
            previous_week_close as (
              select stock_symbol
              , close_price
              , Lead(close_price) OVER (
                ORDER BY stock_symbol, weekly_closing_price) as one_week_later_close_price
              , weekly_closing_price as close_date 
              from weekly_stock_openings 
              where weekly_closing_price is not null 
            )
            
            select  
            prediction_testing.stock_symbol
            , current_week as buy_week
            , prediction_testing.current_close_price as buy_price
            , prediction_date
            , prediction_testing.predicted_close_price
            , predicted_price_change
            , previous_week_close.one_week_later_close_price as cashout_price
            , predicted_price_change_percentage
            , prediction_testing.keyword
            , prediction_testing.time_delay
            , prediction_testing.filing_type
            , prediction_testing.start_date
            
            from prediction_testing
            join previous_week_close on prediction_testing.current_week = previous_week_close.close_date
            and prediction_testing.stock_symbol = previous_week_close.stock_symbol
            where previous_week_close.close_date >= '2022-07-01'
            and predicted_close_price > current_close_price
            '''
        buy_df_results = pd.read_sql(buy_recommendation, con=connect)
        buy_df_results['predicted_price_change_percentage'] = buy_df_results['predicted_price_change_percentage'].apply(format_percent)
        df_for_pg_upload.append(buy_df_results, ignore_index=True)
        print(buy_df_results)
    print(df_for_pg_upload)

# backtesting()