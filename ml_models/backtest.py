import pandas as pd
from datetime import date, timedelta
from sqlalchemy import create_engine
import psycopg2
import passwords
import older_versions.forecast_top_stocks_model as forecast_top_stocks_model

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

def backtesting_buy_recommendation_list():
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
        buy_df_results = pd.read_sql(buy_recommendation, con=connect)
        if buy_df_results.empty:
            continue
        else:
            buy_df_results['predicted_price_change_percentage'] = buy_df_results['predicted_price_change_percentage'].apply(format_percent)
            df_recommended_buys.append(buy_df_results)
    df_for_pg_upload = pd.concat(df_recommended_buys, ignore_index=True)
    df_for_pg_upload = df_for_pg_upload.sort_values(by=['buy_week', 'stock_symbol'])
    print(df_for_pg_upload)
    # append_to_postgres(df_for_pg_upload, 'backtest_buys_test', 'replace')
    return df_for_pg_upload

# backtesting_buy_recommendation_list()

def calculate_returns():
    cash_in_hand = 1000

    query_for_buys = f'''
    with stock_selections as (
      SELECT
          stock_symbol,
          buy_week,
          buy_price,
          cashout_price,
          CAST(REPLACE(MAX(predicted_price_change_percentage), '%%', '') AS FLOAT)/100 AS predicted_price_change_percentage
      FROM
          backtest_buys_test
      group by stock_symbol, buy_week, buy_price, cashout_price
    ),
    
    total_estimation as (
      select buy_week, sum(predicted_price_change_percentage) as total_change_amount
      from stock_selections
      group by buy_week
    )
    
    select 
      stock_symbol, 
      stock_selections.buy_week, 
      buy_price, 
      cashout_price,
      predicted_price_change_percentage / total_change_amount as scaled_predicted_change
    from 
      stock_selections 
      join total_estimation on stock_selections.buy_week = total_estimation.buy_week
    where predicted_price_change_percentage != 0
    order by 
      buy_week asc
        '''
    df_for_buys = pd.read_sql(query_for_buys, con=connect)

    performance_at_each_week = []
    # Iterate through each unique buy_week date and calculate returns
    for date in df_for_buys['buy_week'].unique():
        df_for_date = df_for_buys[df_for_buys['buy_week'] == date]

        returns_for_date = (((cash_in_hand * df_for_date['scaled_predicted_change']) / df_for_date['buy_price'] ) *
        df_for_date['cashout_price']).sum()

        cash_in_hand = returns_for_date
        end_of_week_performance = (date, cash_in_hand)
        performance_at_each_week.append(end_of_week_performance)
    performance_at_each_week_df = pd.DataFrame(performance_at_each_week, columns=['week_of_purchases', 'portfolio_value'])
    return cash_in_hand, performance_at_each_week_df

# calculate_returns()

def comparing_returns_vs_sandp():
    returns_df = calculate_returns()[1]
    first_date = returns_df['week_of_purchases'].min()
    last_date = returns_df['week_of_purchases'].max()

    sandp_query = f'''
    select created_at as week_of_purchases, close_price as s_and_p_price from ticker_data
    where stock_symbol = '^SP500TR'
    and created_at >= '{first_date}'
    and created_at <= '{last_date}'
    '''
    df_for_join = pd.read_sql(sandp_query, con=connect)
    df_for_join['week_of_purchases'] = pd.to_datetime(df_for_join['week_of_purchases'])
    returns_df['week_of_purchases'] = pd.to_datetime(returns_df['week_of_purchases'])
    df_for_chart = pd.merge(df_for_join, returns_df, how='inner', on='week_of_purchases')

    return df_for_chart