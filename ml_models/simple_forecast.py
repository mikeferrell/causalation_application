import numpy as np
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta, datetime
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sqlalchemy import create_engine
import psycopg2
import passwords


url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

training_dataset = f'''
        with prepped_data as (with matched_dates as (
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
    
    select md1.stock_date, md1.close_price, md2.filing_week, md2.keyword_mentions_rolling_avg
    from matched_dates as md1
    join matched_dates as md2 
    on md1.stock_date = md2.filing_week + interval '1 week'
    offset 3
    )
    
    select (EXTRACT(YEAR FROM filing_week) * 10000) + (EXTRACT(MONTH FROM filing_week) * 100) + EXTRACT(DAY FROM filing_week) AS filing_week
    , keyword_mentions_rolling_avg, close_price
    from prepped_data
        '''
df_results = pd.read_sql(training_dataset, con=connect)

# load the data into a Pandas DataFrame
# df = pd.read_csv('/Users/michaelferrell/PycharmProjects/causalation_dashboard/ml_models/stock_and_keywords.csv')

# select the target variable and input features
X = df_results.drop(columns=['filing_week', 'keyword_mentions_rolling_avg'])
y = df_results['close_price']

# split the data into a training set and a test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# create the random forest model
model = RandomForestRegressor(n_estimators=200, max_depth=10)

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
    
    select (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) AS filing_week
    , md2.keyword_mentions_rolling_avg, md1.close_price
    from matched_dates as md1
    join matched_dates as md2 
    on md1.stock_date = md2.filing_week + interval '1 week'
    where md2.filing_week = '2022-12-05'
    '''
df_test = pd.read_sql(test_dataset, con=connect)

# select the input features for the prediction
X_pred = df_test.drop(columns=['filing_week', 'keyword_mentions_rolling_avg'])

# use the trained model to make a prediction
prediction = model.predict(X_pred)

# print the prediction
print('Predicted stock price:', prediction)






# # from keras.models import Sequential
# # from keras.layers import LSTM, Dense
#
#
# url = passwords.rds_access
# engine = create_engine(url)
# connect = engine.connect()
#
# stock_query_results = f'''
#         select * from ticker_data
#         WHERE stock_symbol = 'GME'
#         and created_at >= '2022-01-01'
#         and created_at <= '2022-11-01'
#     '''
#
# stock_query_test = f'''
#         select * from ticker_data
#         WHERE stock_symbol = 'GME'
#         and created_at >= '2022-11-02'
#         and created_at <= '2022-12-02'
#     '''
#
# keyword_query_results = f'''
#         with keyword_words as (SELECT
#             date(filing_date) as filing_date,
#               round(
#                 length(risk_factors) - length(REPLACE(risk_factors, 'cloud', ''))
#               ) / length('cloud') AS keyword_count
#             FROM
#               public.edgar_data
#             WHERE filing_date >= '2022-01-01'
#             and filing_date <= '2022-11-01'
#             )
#
#             select 'cloud' as keywords,
#             sum(keyword_count) as keyword_count
#             from keyword_words
#             where keyword_count > 0
#             group by 1
#     '''
#
# keyword_query_test = f'''
#         with keyword_words as (SELECT
#             date(filing_date) as filing_date,
#               round(
#                 length(risk_factors) - length(REPLACE(risk_factors, 'cloud', ''))
#               ) / length('cloud') AS keyword_count
#             FROM
#               public.edgar_data
#             WHERE filing_date >= '2022-11-02'
#             and filing_date <= '2022-12-02'
#             )
#
#             select 'cloud' as keywords,
#             sum(keyword_count) as keyword_count
#             from keyword_words
#             where keyword_count > 0
#             group by 1
#     '''
#
#
# # Load the data
# X_train = pd.read_sql(stock_query_results, con=connect)
# y_train = pd.read_sql(keyword_query_results, con=connect)
# X_test = pd.read_sql(stock_query_test, con=connect)
# y_test = pd.read_sql(keyword_query_test, con=connect)
#
# # Build the model
# model = RandomForestRegressor(n_estimators=100)
#
# # Train the model
# model.fit(X_train, y_train)
#
# # Make predictions
# y_pred = model.predict(X_test)
#
# # Evaluate the model
# print(mean_squared_error(y_test, y_pred))
#


#this code works. In order to make it work with queries: return one dataframe with the date (as a number, not a date),
# the stock prices, and the keyword percentages. Then return a new dataframe with just the date and keyword mentions for
#the next week(s) where we want predictions.
#We need to figure out a way to handle missing values in both stocks and keywords.
# impute the missing values using techniques like linear interpolation or mean imputation.
# also, recongize that adding a week was doing everything in reverse and having the stocks come before the keywords.
#we need to subtract a week from all queries



