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


filing_weeks = f'''
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
          -- - interval '1 week'
          where first_price_in_week >= '2021-02-01'
          and first_price_in_week <= '2022-12-12'
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
        where md2.filing_week >= '2022-10-01'
        '''
datetime_list = []
df_filing_weeks = pd.read_sql(filing_weeks, con=connect)
df_filing_weeks = df_filing_weeks['filing_week'].tolist()
for timestamp in df_filing_weeks:
    datetime_list.append(timestamp.strftime("%Y-%m-%d"))


training_dataset = f'''
        with prepped_data as (with matched_dates as (
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
      and first_price_in_week <= '2022-12-12'
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

test_results = []
full_test_data = []

for dates in datetime_list:
    test_dataset = f'''
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
          -- - interval '1 week'
          where first_price_in_week >= '2021-02-01'
          and first_price_in_week <= '2022-12-12'
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

        select (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) AS filing_week_int
        , md2.filing_week::date, md2.keyword_mentions_rolling_avg, md1.close_price, md1.stock_date
        from matched_dates as md1
        join matched_dates as md2
        on md1.stock_date = md2.filing_week + interval '1 week'
        where md2.filing_week = '{dates}'
        '''
    df_test_full = pd.read_sql(test_dataset, con=connect)
    df_test = df_test_full.drop(columns=['filing_week', 'stock_date'])
    # df_test['stock_date'] = sum(int(dates), int(7))
    test_results.append(df_test)
    full_test_data.append(df_test_full)

test_results_df = pd.concat(test_results, ignore_index=True)
df_test = pd.DataFrame(test_results_df)

full_results_df = pd.concat(full_test_data, ignore_index=True)
df_full = pd.DataFrame(full_results_df)


# select the input features for the prediction
X_pred = df_test.drop(columns=['filing_week_int', 'keyword_mentions_rolling_avg'])

# use the trained model to make a prediction
prediction = model.predict(X_pred)
print('Predicted stock price:', prediction)

df_full['predictions'] = prediction
print(df_full)




