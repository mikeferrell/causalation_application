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


def calculate_top_five_forecasts():
    df_for_pg_upload = pd.DataFrame(columns=['current_week', 'stock_date', 'keyword_mentions_rolling_avg',
                                             'current_close_price', 'next_week_close_price', 'predicted_price',
                                             'stock_symbol', 'keyword', 'start_date', 'time_delay', 'filing_type'])

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

    row_range = range(0, 6)
    for rows in row_range:
        df_row = query_df.iloc[rows]
        stock_symbol = df_row['stock_symbol']
        keyword = df_row['keyword']
        correlation_start_date = df_row['start_date']
        interval = df_row['time_delay']
        filing_type = df_row['filing_type']

        filing_weeks = f'''
                with matched_dates as (
                  with rolling_average_calculation as (
                  with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                  stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null )
        
                  select 
                  distinct weekly_closing_price as stock_date
                  , filing_week
                  , close_price
                  , stock_symbol
                  , 1.00 * keyword_mentions / total_filings as keyword_percentage
                  from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week 
                  where weekly_closing_price >= '2017-01-01'
                  and filing_type = '{filing_type}'
                  and stock_symbol = '{stock_symbol}'
                  order by stock_symbol, stock_date asc
                  )
        
                  select stock_date
                  , stock_symbol
                  , close_price
                    , filing_week
                  , '{keyword} Mentions' as keyword_mentions
                  , avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                  from rolling_average_calculation
                  order by stock_symbol, stock_date asc
                  )
        
                select
                md2.filing_week 
                from matched_dates as md1
                join matched_dates as md2 
                on md1.stock_date = md2.filing_week + interval '{interval} week'
                where md2.filing_week >= '{correlation_start_date}'
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
                              with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                            stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null )
        
                            select 
                            distinct weekly_closing_price as stock_date
                            , filing_week
                            , close_price
                            , stock_symbol
                            , 1.00 * keyword_mentions / total_filings as keyword_percentage
                            from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week 
                            where weekly_closing_price >= '2017-01-01'
                            and filing_type = '{filing_type}'
                            and stock_symbol = '{stock_symbol}'
                            order by stock_symbol, stock_date asc
                            )
        
                            select stock_date
                            , stock_symbol
                            , close_price
                              , filing_week
                            , '{keyword} Mentions' as keyword_mentions
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
                            on md1.stock_date = md2.filing_week + interval '{interval} week'
                            where md2.filing_week < '{dates}'
                            offset 3
                    '''
            df_results = pd.read_sql(training_dataset, con=connect)
            try:
                X = df_results.drop(columns=['next_week_close_price'])
                y = df_results['next_week_close_price']
                X = X.interpolate()
                y = y.interpolate()
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=12)

                # create the random forest model
                # model = DecisionTreeRegressor(criterion='friedman_mse', random_state=12)
                # model = RandomForestRegressor(n_estimators=200, max_depth=20)
                model = LinearRegression()

                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                print('Mean absolute error:', mae)

                test_dataset = f'''
                            with matched_dates as (
                            with rolling_average_calculation as (
                              with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                            stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null )
            
                            select 
                            distinct weekly_closing_price as stock_date
                            , filing_week
                            , close_price
                            , stock_symbol
                            , 1.00 * keyword_mentions / total_filings as keyword_percentage
                            from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week 
                            where weekly_closing_price >= '2017-01-01'
                            and filing_type = '{filing_type}'
                            and stock_symbol = '{stock_symbol}'
                            order by stock_symbol, stock_date asc
                            )
            
                            select stock_date
                            , stock_symbol
                            , close_price
                              , filing_week
                            , '{keyword} Mentions' as keyword_mentions
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
                            on md1.stock_date = md2.filing_week + interval '{interval} week'
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
            except (KeyError, ValueError) as error1:
                print(error1)
            continue

        df_test = pd.DataFrame(test_results, columns=['predicted_price'])
        full_results_df = pd.concat(full_test_data, ignore_index=True)
        df_full = pd.DataFrame(full_results_df)
        df_full['predicted_price'] = df_test
        df_full['stock_symbol'] = stock_symbol
        df_full['keyword'] = keyword
        df_full['start_date'] = correlation_start_date
        df_full['time_delay'] = interval
        df_full['filing_type'] = filing_type
        df_full = df_full.drop_duplicates()
        df_for_pg_upload = df_for_pg_upload.append(df_full, ignore_index=True)
    return df_for_pg_upload

# full_df_for_upload = calculate_top_five_forecasts()
# append_to_postgres(full_df_for_upload, 'top_five_prediction_results', 'replace')


