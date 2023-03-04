import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import time
import passwords
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import forecast_top_stocks_model
from sqlalchemy import create_engine
import psycopg2

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

#current issues: looks like 'next week close price' is the price that aligns with week_opening_date. I want to drop
#current_week and current_close_price since those are last week. First, need to ensure the model is trained with the dates
#in the right place for what I want.
#next, getting a lot of errors for "next week buys". figure out why so many lack data. are
def weekly_buy_recommendation_list():
    df_for_pg_upload = pd.DataFrame(columns=['current_week', 'week_opening_date', 'keyword_mentions_rolling_avg',
                                             'current_close_price', 'next_week_close_price', 'predicted_price',
                                             'stock_symbol', 'keyword', 'start_date', 'time_delay', 'filing_type'])
    query_df = forecast_top_stocks_model.top_correlation_query_results()

    row_range = range(0, 10)
    for rows in row_range:
        df_row = query_df.iloc[rows]
        stock_symbol = df_row['stock_symbol']
        keyword = df_row['keyword']
        correlation_start_date = df_row['start_date']
        interval = df_row['time_delay']
        filing_type = df_row['filing_type']
        end_date = df_row['end_date']

        test_results = []
        full_test_data = []
        mae_data = []
        future_predictions = []

        datetime_list = forecast_top_stocks_model.list_of_filing_weeks_for_training(keyword, filing_type, stock_symbol,
                                                                                    interval, correlation_start_date)
        most_recent_date = datetime_list.pop()

        try:
            df_test_full, df_test, mae, model = forecast_top_stocks_model.train_ml_model(keyword, filing_type,
                                                                                         stock_symbol, interval,
                                                                                         most_recent_date)
            full_test_data.append(df_test_full)
            mae_data.append(mae)

            try:
                prediction = model.predict(df_test)
                test_results.append(prediction)
                print('Predicted stock price:', prediction)
            except (KeyError, ValueError) as error:
                print(error)
                continue
        except (KeyError, ValueError) as error1:
            print(error1)
            continue

        data_for_predicting_next_week = f'''
                    with most_recent_close_price as (
                      select created_at, close_price from public.ticker_data 
                      where stock_symbol = '{stock_symbol}'
                      and created_at = '{end_date}'
                    ),
                    
                    most_recent_keyword_mention_rolling_average as (
                      with rolling_average_calculation as ( 
                       with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
                        stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null)
                    
                        select 
                        week_opening_date
                        , week_close_price
                        , stock_symbol
                        , 1.00 * keyword_mentions / total_filings as keyword_percentage
                        from stock_weekly_opening 
                        inner join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week + '{interval}  week'
                        where week_opening_date >= '{correlation_start_date}'
                        and week_opening_date <= '{end_date}'
                        and filing_type != '{filing_type}'
                        and stock_symbol = '{stock_symbol}'
                      )
                    
                      select week_opening_date, stock_symbol,
                      week_close_price,
                      'keyword Mentions' as keyword_mentions,
                      avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                      from rolling_average_calculation
                      order by stock_symbol, week_opening_date asc
                    )
                      
                    select 
                    (EXTRACT(YEAR FROM r_a.week_opening_date) * 10000) + (EXTRACT(MONTH FROM r_a.week_opening_date) * 100) + EXTRACT(DAY FROM r_a.week_opening_date) as current_week
                    , r_a.keyword_mentions_rolling_avg 
                    , r_c.close_price as current_close_price
                    from most_recent_keyword_mention_rolling_average as r_a, most_recent_close_price as r_c
                    offset (select count(week_opening_date) - 1 from most_recent_keyword_mention_rolling_average)
                    '''
        df_for_predicting_next_week = pd.read_sql(data_for_predicting_next_week, con=connect)
        print(df_for_predicting_next_week)
        try:
            future_prediction = model.predict(df_for_predicting_next_week)
            future_predictions.append(future_prediction)
            print('next_week_buys:', future_prediction)
        except (KeyError, ValueError) as error:
            print(error)
            continue

        df_future_predictions = pd.DataFrame(future_predictions, columns=['predicted_price'])
        full_results_df = pd.concat(full_test_data, ignore_index=True)
        df_full = pd.DataFrame(full_results_df)
        df_full['predicted_price'] = df_future_predictions
        df_full['stock_symbol'] = stock_symbol
        df_full['keyword'] = keyword
        df_full['start_date'] = correlation_start_date
        df_full['time_delay'] = interval
        df_full['filing_type'] = filing_type
        df_full = df_full.drop_duplicates()
        df_for_pg_upload = df_for_pg_upload.append(df_full, ignore_index=True)

    df_for_pg_upload = df_for_pg_upload.drop(columns=['current_week', 'keyword_mentions_rolling_avg',
                                                      'current_close_price'])
    df_for_pg_upload.rename(columns={'next_week_close_price': 'previous_weekly_close_price'}, inplace=True)
    df_for_pg_upload.rename(columns={'week_opening_date': 'previous_weekly_open_date'}, inplace=True)
    df_for_pg_upload.rename(columns={'predicted_price': 'predicted_weekly_close_price'}, inplace=True)
    return df_for_pg_upload

full_df_for_upload = weekly_buy_recommendation_list()
forecast_top_stocks_model.append_to_postgres(full_df_for_upload, 'future_buy_recommendations', 'replace')

