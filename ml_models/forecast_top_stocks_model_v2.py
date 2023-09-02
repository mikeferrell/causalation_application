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
    one_year_ago = today - timedelta(days=365)
    one_year_ago = str(one_year_ago)
    oya_year = int(one_year_ago[0:4])
    oya_month = int(one_year_ago[5:7])
    oya_day = int(one_year_ago[8:10])

    yesterday = str(date(y_year, y_month, y_day))
    one_year_ago = str(date(oya_year, oya_month, oya_day))
    return yesterday, one_year_ago


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


# this is the list of the top 25 correlations from the all_correlation_scores table, with some filtering
#this only works for this week, not last week. if we want to add last week into the dash, we need to fix this
def top_correlation_query_results(table_for_this_week_or_last):
    top_correlation_query_results = f'''
    with top_absolute_scores AS (
      with correlated as (select stock_symbol
      , split_part("Keyword", ' Mentions', 1) as keyword
      , start_date
      , end_date
      , time_delay
      , filing_type
      , correlation
      , abs(correlation) as abs_corr
      from public.all_correlation_scores
      where correlation is not null
        and date(start_date) <= current_date - interval '40 week'
        and stock_symbol not in ('GEHC', 'CAH', 'DDOG')
        and abs(correlation) != 1
        and "Keyword" != 'cryptocurrency Mentions'
        and time_delay != '8'
      order by correlation desc
      limit 250),
      
      inverse as (
      select stock_symbol
      , split_part("Keyword", ' Mentions', 1) as keyword
      , start_date
      , end_date
      , time_delay
      , filing_type
      , correlation
      , abs(correlation) as abs_corr
      from public.all_inverse_correlation_scores
      where correlation is not null
        and date(start_date) <= current_date - interval '40 week'
        and stock_symbol not in ('GEHC', 'CAH', 'DDOG')
        and abs(correlation) != 1
        and "Keyword" != 'cryptocurrency Mentions'
        and time_delay != '8'
      order by correlation asc
      limit 250
      )
      
      select * from correlated
      union all
      select * from inverse 
      order by abs_corr desc
      )
      
    select distinct on (stock_symbol) *
    from top_absolute_scores
    order by stock_symbol, abs_corr desc
    '''
    query_df = pd.read_sql(top_correlation_query_results, con=connect)
    query_df = query_df.sort_values(by=['abs_corr'], ascending=False)
    query_df = query_df.head(25)
    query_df = query_df.drop(columns=['abs_corr'])
    return query_df


def list_of_filing_weeks_for_training(keyword, filing_type, stock_symbol, interval, correlation_start_date):
    filing_weeks = f'''
            with matched_dates as (
              with rolling_average_calculation as (
              with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
              stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null )

              select 
              distinct week_opening_date
              , filing_week
              , week_close_price
              , stock_symbol
              , 1.00 * keyword_mentions / total_filings as keyword_percentage
              from stock_weekly_opening join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week 
              where week_opening_date >= '2017-01-01'
              and filing_type = '{filing_type}'
              and stock_symbol = '{stock_symbol}'
              order by stock_symbol, week_opening_date asc
              )

              select week_opening_date
              , stock_symbol
              , week_close_price
                , filing_week
              , '{keyword} Mentions' as keyword_mentions
              , avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
              from rolling_average_calculation
              order by stock_symbol, week_opening_date asc
              )

            select
            md2.filing_week 
            from matched_dates as md1
            join matched_dates as md2 
            on md1.week_opening_date = md2.filing_week + interval '{interval} week'
            where md2.filing_week >= '{correlation_start_date}'
            '''
    df_filing_weeks = pd.read_sql(filing_weeks, con=connect)
    df_filing_weeks = df_filing_weeks['filing_week'].tolist()

    datetime_list = []
    for timestamp in df_filing_weeks:
        datetime_list.append(timestamp.strftime("%Y-%m-%d"))
    return datetime_list


# this is the model training used all of the charts & tables up to 3/24/23
def train_ml_model(keyword, filing_type, stock_symbol, interval, dates, correlation_start_date):
    training_dataset = f'''
                     with matched_dates as (
                     with rolling_average_calculation as (
                       with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                     stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null )

                     select 
                     distinct week_opening_date
                     , filing_week
                     , week_close_price
                     , stock_symbol
                     , 1.00 * keyword_mentions / total_filings as keyword_percentage
                     from stock_weekly_opening join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week 
                     where week_opening_date >= '{correlation_start_date}'
                     and filing_type = '{filing_type}'
                     and stock_symbol = '{stock_symbol}'
                     order by stock_symbol, week_opening_date asc
                     )

                     select week_opening_date
                     , stock_symbol
                     , week_close_price
                       , filing_week
                     , '{keyword} Mentions' as keyword_mentions
                     , avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                     from rolling_average_calculation
                     order by stock_symbol, week_opening_date asc
                     )

                     select 
                     (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) as current_week
                     , md2.keyword_mentions_rolling_avg
                     , md2.week_close_price as current_close_price
                     , md1.week_close_price as next_week_close_price
                     from matched_dates as md1
                     join matched_dates as md2 
                     on md1.week_opening_date = md2.filing_week + interval '{interval} week'
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

        # choose your model
        model = DecisionTreeRegressor(criterion='friedman_mse', random_state=12)
        # model = RandomForestRegressor(n_estimators=200, max_depth=20)
        # model = LinearRegression()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        print('Mean absolute error:', mae)

        test_dataset = f'''
                     with matched_dates as (
                     with rolling_average_calculation as (
                       with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                     stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null )

                     select 
                     distinct week_opening_date
                     , filing_week
                     , week_close_price
                     , stock_symbol
                     , 1.00 * keyword_mentions / total_filings as keyword_percentage
                     from stock_weekly_opening join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week 
                     where week_opening_date >= '{correlation_start_date}'
                     and filing_type = '{filing_type}'
                     and stock_symbol = '{stock_symbol}'
                     order by stock_symbol, week_opening_date asc
                     )

                     select week_opening_date
                     , stock_symbol
                     , week_close_price
                       , filing_week
                     , '{keyword} Mentions' as keyword_mentions
                     , avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                     from rolling_average_calculation
                     order by stock_symbol, week_opening_date asc
                     )

                     select 
                     (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) as current_week
                     , md1.week_opening_date
                     , md2.keyword_mentions_rolling_avg
                     , md2.week_close_price as current_close_price
                     , md1.week_close_price as next_week_close_price
                     from matched_dates as md1
                     join matched_dates as md2 
                     on md1.week_opening_date = md2.filing_week + interval '{interval} week'
                     where md2.filing_week = '{dates}'
                     '''
        df_test_full = pd.read_sql(test_dataset, con=connect)
        df_test = df_test_full.drop(columns=['week_opening_date', 'next_week_close_price'])
        df_test_full = df_test_full.drop_duplicates()
        df_test = df_test.drop_duplicates()
    except (KeyError, ValueError) as error1:
        print(error1)
    return df_test_full, df_test, mae, model


# This function will only use the data points within the period we observe strong correlation, and then try to
# predict the next week. this will be used for the precise backtest
def train_narrow_ml_model(keyword, filing_type, stock_symbol, interval, end_date, correlation_start_date, model_type):
    training_dataset = f'''
                     with matched_dates as (
                     with rolling_average_calculation as (
                       with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                     stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null )

                     select 
                     distinct week_opening_date
                     , week_close_price
                     , stock_symbol
                     , 1.00 * keyword_mentions / total_filings as keyword_percentage
                     from stock_weekly_opening 
                     join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week
                     where week_opening_date >= '{correlation_start_date}'
                     and filing_type = '{filing_type}'
                     and stock_symbol = '{stock_symbol}'
                     order by stock_symbol, week_opening_date asc
                     )

                     select week_opening_date
                     , stock_symbol
                     , week_close_price
                     , '{keyword} Mentions' as keyword_mentions
                     , avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                     from rolling_average_calculation
                     order by stock_symbol, week_opening_date asc
                     )

                     select 
                     (EXTRACT(YEAR FROM md2.week_opening_date) * 10000) + (EXTRACT(MONTH FROM md2.week_opening_date) * 100) + EXTRACT(DAY FROM md2.week_opening_date) as current_week
                     , md2.keyword_mentions_rolling_avg
                     , md2.week_close_price as current_close_price
                     , md1.week_close_price as next_week_close_price
                     from matched_dates as md1
                     join matched_dates as md2 
                     on md1.week_opening_date = md2.week_opening_date + interval '{interval} week'
                     where md2.week_opening_date < '{end_date}'
                     offset 3
             '''
    df_results = pd.read_sql(training_dataset, con=connect)
    try:
        # next_week_close_price should be called close_price_after_time_interval_in_the_future
        X = df_results.drop(columns=['next_week_close_price'])
        y = df_results['next_week_close_price']
        X = X.interpolate()
        y = y.interpolate()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=12)

        # choose your model
        if model_type == 'decision_tree':
            model = DecisionTreeRegressor(criterion='friedman_mse', random_state=12)
        elif model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=200, max_depth=20)
        else:
            model = LinearRegression()

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        print('Mean absolute error:', mae)

        test_dataset = f'''
                     with matched_dates as (
                     with rolling_average_calculation as (
                       with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}' and filing_type = '{filing_type}'),
                     stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null )

                     select 
                     distinct week_opening_date
                     , week_close_price
                     , stock_symbol
                     , 1.00 * keyword_mentions / total_filings as keyword_percentage
                     from stock_weekly_opening 
                     join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week
                     where week_opening_date >= '{correlation_start_date}'
                     and filing_type = '{filing_type}'
                     and stock_symbol = '{stock_symbol}'
                     order by stock_symbol, week_opening_date asc
                     )

                     select week_opening_date
                     , stock_symbol
                     , week_close_price
                     , '{keyword} Mentions' as keyword_mentions
                     , avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                     from rolling_average_calculation
                     order by stock_symbol, week_opening_date asc
                     )

                     select 
                     (EXTRACT(YEAR FROM md2.week_opening_date) * 10000) + (EXTRACT(MONTH FROM md2.week_opening_date) * 100) + EXTRACT(DAY FROM md2.week_opening_date) as current_week
                     , md1.week_opening_date as prediction_date
                     , md2.week_opening_date
                     , md2.keyword_mentions_rolling_avg
                     , md2.week_close_price as current_close_price
                     , md1.week_close_price as next_week_close_price
                     from matched_dates as md1
                     join matched_dates as md2 
                     on md1.week_opening_date = md2.week_opening_date + interval '{interval} week'
                     where md2.week_opening_date = '{end_date}'
                     '''
        df_test_full = pd.read_sql(test_dataset, con=connect)
        df_test = df_test_full.drop(columns=['week_opening_date', 'prediction_date', 'next_week_close_price'])
        df_test_full = df_test_full.drop_duplicates()
        df_test = df_test.drop_duplicates()
    except (KeyError, ValueError) as error1:
        print(error1)
    return df_test_full, df_test, mae, model


# if this is returning empty dataframes, then it's because there's some new stock that entered the S&P that doesn't have
# enough data to create a 12 week rolling average (and therefore the later queries in this function return no results)
# to fix, run top_correlation_query_results against the DB and see what the top results are, then add that stock to the
# where clause to supress it
def calculate_top_ten_forecasts(testing_timeline):
    yesterday, one_year_ago = defined_dates()
    df_for_pg_upload = pd.DataFrame(columns=['current_week', 'week_opening_date', 'keyword_mentions_rolling_avg',
                                             'current_close_price', 'next_week_close_price', 'predicted_price',
                                             'stock_symbol', 'keyword', 'start_date', 'time_delay', 'filing_type'])

    query_df = top_correlation_query_results()

    row_count = query_df.shape[0]
    row_range = range(0, row_count)
    for rows in row_range:
        df_row = query_df.iloc[rows]
        stock_symbol = df_row['stock_symbol']
        keyword = df_row['keyword']
        correlation_start_date = df_row['start_date']
        interval = df_row['time_delay']
        filing_type = df_row['filing_type']

        # calling function to determing the end date for each loop for the model to use for the training set
        # this ensures that, when backtesting, the real data isn't appearing in the training set
        # when running this one time, just set datetime list as 'yesterday'
        if testing_timeline == 'backtest':
            datetime_list = list_of_filing_weeks_for_training(keyword, filing_type, stock_symbol, interval,
                                                              correlation_start_date)
        else:
            datetime_list = [yesterday]

        test_results = []
        full_test_data = []
        mae_data = []

        for dates in datetime_list:
            df_test_full, df_test, mae, model = train_ml_model(keyword, filing_type, stock_symbol,
                                                               interval, dates, correlation_start_date)
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

#
# full_df_for_upload = calculate_top_ten_forecasts('backtest')
# print(full_df_for_upload)
# append_to_postgres(full_df_for_upload, 'top_five_prediction_results', 'replace')


def weekly_buy_recommendation_list(this_week_or_last):
    # this_week_or_next = 'this week'

    df_for_pg_upload = pd.DataFrame(columns=['current_week', 'week_opening_date', 'keyword_mentions_rolling_avg',
                                             'current_close_price', 'next_week_close_price', 'predicted_price',
                                             'stock_symbol', 'keyword', 'start_date', 'time_delay', 'filing_type'])

    # setting this up to display last weeks top 10 correlations. need to first ensure that data exists in a table
    # since it doesn't exist in all_correlation_scores. Then, need to write that query, then need to ensure the columns
    # line up with the current query
    if this_week_or_last == 'this week':
        query_df = top_correlation_query_results('all_correlation_scores')
    else:
        query_df = top_correlation_query_results('last_week_correlation_scores')

    row_count = query_df.shape[0]
    row_range = range(0, row_count)
    # print(query_df)
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

        datetime_list = list_of_filing_weeks_for_training(keyword, filing_type, stock_symbol,
                                                          interval, correlation_start_date)
        # print(datetime_list)
        most_recent_date = datetime_list.pop()

        try:
            # print(keyword, filing_type, stock_symbol, interval, most_recent_date, correlation_start_date)
            df_test_full, df_test, mae, model = train_ml_model(keyword, filing_type, stock_symbol, interval,
                                                               most_recent_date, correlation_start_date)
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
        # print(df_for_predicting_next_week)
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
    df_for_pg_upload.rename(columns={'next_week_close_price': 'previous_weekly_close_price',
                                     'week_opening_date': 'previous_weekly_open_date',
                                     'predicted_price': 'predicted_weekly_close_price'}, inplace=True)
    return df_for_pg_upload


#
# df_for_upload = weekly_buy_recommendation_list('this week')
# print(df_for_upload)
# append_to_postgres(df_for_upload, 'future_buy_recommendations', 'replace')



##THis doesn't appear to be used anywhere. Maybe delete?
def calculate_purchase_amounts(principal):
    query_for_buys = f'''
    with stock_selections as (
      SELECT
          stock_symbol,
          previous_weekly_open_date,
          previous_weekly_close_price,
          predicted_weekly_close_price, 
          (predicted_weekly_close_price / previous_weekly_close_price) - 1 AS predicted_price_change_percentage
      FROM
          public.future_buy_recommendations
      WHERE predicted_weekly_close_price > previous_weekly_close_price
      order by predicted_price_change_percentage desc
      limit 5
    ),

    total_estimation as (
      select previous_weekly_open_date, sum(predicted_price_change_percentage) as total_change_amount
      from stock_selections
      group by previous_weekly_open_date
    )

    select 
      stock_symbol
      , previous_weekly_close_price
      , ({principal} * (predicted_price_change_percentage / total_change_amount)) / previous_weekly_close_price as number_of_shares_to_purchase
      , predicted_price_change_percentage / total_change_amount as scaled_predicted_change
    from 
      stock_selections 
      join total_estimation on stock_selections.previous_weekly_open_date = total_estimation.previous_weekly_open_date
    where predicted_price_change_percentage != 0
    order by 
     stock_symbol asc
        '''
    df_for_buys = pd.read_sql(query_for_buys, con=connect)
    return df_for_buys