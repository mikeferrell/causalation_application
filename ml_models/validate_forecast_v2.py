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

def window_input_output(input_length: int, data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    i = 1
    while i < input_length:
        df[f'x_{i}'] = df['current_close_price'].shift(i)
        i = i + 1
    j = 1
    while j < input_length:
        df[f'y_{j}'] = df['keyword_mentions_rolling_avg'].shift(j)
        j = j + 1
    df = df.dropna(axis=0)
    return df


filing_weeks = f'''
        with matched_dates as (
          with rolling_average_calculation as (
          with keyword_data as (select * from keyword_weekly_counts where keyword = 'war'),
          stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null )

          select 
          distinct weekly_closing_price as stock_date
          , filing_week
          , close_price
          , stock_symbol
          , 1.00 * keyword_mentions / total_filings as keyword_percentage
          from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week 
          -- - interval '1 week'
          where weekly_closing_price >= '2021-02-01'
          and weekly_closing_price <= '2022-12-12'
          and filing_type = '10-Q'
          and stock_symbol = 'CPT'
          order by stock_symbol, stock_date asc
          )

          select stock_date
          , stock_symbol
          , close_price
            , filing_week
          , 'war Mentions' as keyword_mentions
          , avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
          from rolling_average_calculation
          order by stock_symbol, stock_date asc
          )

        select
        md2.filing_week 
        from matched_dates as md1
        join matched_dates as md2 
        on md1.stock_date = md2.filing_week + interval '1 week'
        where md2.filing_week >= '2022-09-01'
        '''
df_filing_weeks = pd.read_sql(filing_weeks, con=connect)
df_filing_weeks = df_filing_weeks['filing_week'].tolist()

datetime_list = []
for timestamp in df_filing_weeks:
    datetime_list.append(timestamp.strftime("%Y-%m-%d"))

test_results = []
full_test_data = []
mae_data = []

for dates in datetime_list:
    training_dataset = f'''
                    with matched_dates as (
                    with rolling_average_calculation as (
                      with keyword_data as (select * from keyword_weekly_counts where keyword = 'war'),
                    stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null )
    
                    select 
                    distinct weekly_closing_price as stock_date
                    , filing_week
                    , close_price
                    , stock_symbol
                    , 1.00 * keyword_mentions / total_filings as keyword_percentage
                    from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week 
                    where weekly_closing_price >= '2021-02-01'
                    and filing_type = '10-Q'
                    and stock_symbol = 'CPT'
                    order by stock_symbol, stock_date asc
                    )
    
                    select stock_date
                    , stock_symbol
                    , close_price
                      , filing_week
                    , 'war Mentions' as keyword_mentions
                    , avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                    from rolling_average_calculation
                    order by stock_symbol, stock_date asc
                    )
    
                    select 
                    (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) as current_week
                    , md2.keyword_mentions_rolling_avg
                    , md2.close_price as current_close_price
                    , md1.close_price as next_week_close_price
                    from matched_dates as md1
                    join matched_dates as md2 
                    on md1.stock_date = md2.filing_week + interval '1 week'
                    where md2.filing_week < '{dates}'
                    offset 3
            '''
    df_results = pd.read_sql(training_dataset, con=connect)
    # multistep_df = window_input_output(2, df_results)
    # print(multistep_df)

    X = df_results.drop(columns=['next_week_close_price'])
    y = df_results['next_week_close_price']
    #fill in missing data
    X = X.interpolate()
    y = y.interpolate()

    # split the data into a training set and a test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=12)

    # create the random forest model
    # model = DecisionTreeRegressor(criterion='friedman_mse', random_state=12)
    # model = RandomForestRegressor(n_estimators=200, max_depth=20)
    model = LinearRegression()

    # fit the model to the training data
    model.fit(X_train, y_train)

    # make predictions on the test data
    y_pred = model.predict(X_test)

    # calculate the mean absolute error
    mae = mean_absolute_error(y_test, y_pred)

    # print the mean absolute error
    print('Mean absolute error:', mae)

    test_dataset = f'''
                with matched_dates as (
                with rolling_average_calculation as (
                  with keyword_data as (select * from keyword_weekly_counts where keyword = 'war'),
                stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null )

                select 
                distinct weekly_closing_price as stock_date
                , filing_week
                , close_price
                , stock_symbol
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week 
                where weekly_closing_price >= '2021-02-01'
                and filing_type = '10-Q'
                and stock_symbol = 'CPT'
                order by stock_symbol, stock_date asc
                )

                select stock_date
                , stock_symbol
                , close_price
                  , filing_week
                , 'war Mentions' as keyword_mentions
                , avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, stock_date asc
                )

                select 
                (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) as current_week
                , md1.stock_date
                , md2.keyword_mentions_rolling_avg
                , md2.close_price as current_close_price
                , md1.close_price as next_week_close_price
                from matched_dates as md1
                join matched_dates as md2 
                on md1.stock_date = md2.filing_week + interval '1 week'
                where md2.filing_week = '{dates}'
                '''
    df_test_full = pd.read_sql(test_dataset, con=connect)
    df_test = df_test_full.drop(columns=['stock_date', 'next_week_close_price'])
    df_test_full = df_test_full.drop_duplicates()
    df_test = df_test.drop_duplicates()
    full_test_data.append(df_test_full)
    mae_data.append(mae)

    try:
        prediction = model.predict(df_test)
        test_results.append(prediction)
        print('Predicted stock price:', prediction)
    except (KeyError, ValueError) as error:
        print(error)
        continue

df_test = pd.DataFrame(test_results, columns=['predicted_price'])
# multistep_df_test = window_input_output(2, df_test)
full_results_df = pd.concat(full_test_data, ignore_index=True)
df_full = pd.DataFrame(full_results_df)
mae_df = pd.DataFrame(mae_data, columns=['mae'])

df_full['predicted_price'] = df_test
# df_full['mae'] = mae_df
df_full = df_full.drop_duplicates()
print(df_full)
append_to_postgres(df_full, 'prediction_results', 'replace')

