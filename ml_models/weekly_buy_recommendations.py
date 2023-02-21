import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import time
import passwords
import forecast_top_stocks_model

#cloned from backtest, need to adjust this to run just the most recent buy recommendations for this week
def weekly_buy_recommendation_list():
    df_recommended_buys = []
    query_df = forecast_top_stocks_model.top_correlation_query_results()

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
          , week_opening_date as prediction_date, predicted_price as next_week_predicted_close, next_week_close_price
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
          , 1 - (current_close_price / predicted_price) as predicted_price_change_percentage 
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

        next_week_close as (
          select stock_symbol
          , week_open_price
          , week_close_price
            , week_opening_date
            , Lead(week_open_price) OVER (
          ORDER BY stock_symbol, week_opening_date) as one_week_later_open_price
          , Lead(week_close_price) OVER (
            ORDER BY stock_symbol, week_opening_date) as one_week_later_close_price
          from weekly_stock_openings 
          where week_opening_date is not null 
        )

        select  
        prediction_testing.stock_symbol
        , current_week as buy_week
        --need to change this to the weekly open!
        , next_week_close.one_week_later_open_price as buy_price
        , next_week_close.one_week_later_close_price as cashout_price
        , prediction_date
        , prediction_testing.predicted_close_price
        , predicted_price_change
        , predicted_price_change_percentage
        , prediction_testing.keyword
        , prediction_testing.time_delay
        , prediction_testing.filing_type
        , prediction_testing.start_date

        from prediction_testing
        join next_week_close on prediction_testing.current_week = next_week_close.week_opening_date
        and prediction_testing.stock_symbol = next_week_close.stock_symbol
        where next_week_close.week_opening_date >= '2022-07-01'
        and predicted_close_price > current_close_price
        --pulling the data necessarily to say buy in a given week
            '''
        buy_df_results = pd.read_sql(buy_recommendation, con=forecast_top_stocks_model.connect)
        if buy_df_results.empty:
            continue
        else:
            buy_df_results['predicted_price_change_percentage'] = buy_df_results[
                'predicted_price_change_percentage'].apply(forecast_top_stocks_model.format_percent)
            df_recommended_buys.append(buy_df_results)
    df_for_pg_upload = pd.concat(df_recommended_buys, ignore_index=True)
    df_for_pg_upload = df_for_pg_upload.sort_values(by=['buy_week', 'stock_symbol'])
    print(df_for_pg_upload)
    # forecast_top_stocks_model.append_to_postgres(df_for_pg_upload, 'backtest_buys_test', 'replace')
    return df_for_pg_upload


# backtesting_buy_recommendation_list()
