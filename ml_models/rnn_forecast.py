from keras.models import Sequential
from keras.layers import GRU, Dense, Dropout
import numpy as np
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta, datetime
import time
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine
import psycopg2
import passwords

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

def rnn_forecast():
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
                    and weekly_closing_price <= '2022-12-05'
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
                    offset 3
                     '''
    df_results = pd.read_sql(training_dataset, con=connect)
    print(df_results)

    # Preprocess the data
    X = df_results[['current_week', 'keyword_mentions_rolling_avg', 'current_close_price']].values
    y = df_results['next_week_close_price'].values

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    # Reshape the data to have a time dimension
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))


    # print(X_train, X_test, y_train, y_test)

    # Build the model
    model = Sequential()
    model.add(GRU(64, input_shape=(1, 3)))
    model.add(Dropout(0.1))
    model.add(Dense(61))
    print(model.summary())

    # Compile the model
    model.compile(optimizer='adam', loss='mean_absolute_error')

    # Fit the model
    model.fit(X_train, y_train, epochs=100, batch_size=32)

    # Evaluate the model
    score = model.evaluate(X_test, y_test, batch_size=32)
    print("Test loss:", score)

    # Prepare the input data
    test_query = f'''
                            with matched_dates as (
                    with rolling_average_calculation as (
                      with keyword_data as (select * from keyword_weekly_counts where keyword = 'war'),
                    stock_weekly_opening as (select * from weekly_stock_openings where first_price_in_week is not null )
                    
                    select 
                    distinct first_price_in_week as stock_date
                    , filing_week
                    , close_price
                    , stock_symbol
                    , 1.00 * keyword_mentions / total_filings as keyword_percentage
                    from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week 
                    where first_price_in_week >= '2021-02-01'
                    and first_price_in_week <= '2022-12-05'
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
                    where md1.filing_week >= '2022-10-01'
                    offset 3
                    '''
    df_results = pd.read_sql(test_query, con=connect)
    df_results = df_results[['current_week', 'keyword_mentions_rolling_avg', 'current_close_price']].values
    df_results = np.reshape(df_results, (df_results.shape[0], 1, df_results.shape[1]))

    # Make predictions
    predictions = model.predict(df_results)
    print(predictions)

