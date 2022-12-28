import numpy as np
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta, datetime
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sqlalchemy import create_engine
import psycopg2
import passwords

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


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

training_dataset = f'''
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
                offset 3
        '''
df_results = pd.read_sql(training_dataset, con=connect)
multistep_df = window_input_output(10, df_results)
print(multistep_df)

# select the target variable and input features
X = multistep_df.drop(columns=['next_week_close_price'])
y = multistep_df['next_week_close_price']
#fill in missing data
X = X.interpolate()
y = y.interpolate()

# split the data into a training set and a test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# create the random forest model
# model = RandomForestRegressor(n_estimators=200, max_depth=10)
model = DecisionTreeRegressor()

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
                
                select 
                (EXTRACT(YEAR FROM md2.filing_week) * 10000) + (EXTRACT(MONTH FROM md2.filing_week) * 100) + EXTRACT(DAY FROM md2.filing_week) as current_week
                , md2.keyword_mentions_rolling_avg
                , md2.close_price as current_close_price
                , md1.close_price as next_week_close_price
                from matched_dates as md1
                join matched_dates as md2 
                on md1.stock_date = md2.filing_week + interval '1 week'
                where md2.filing_week = '2022-12-05'

    '''
df_test = pd.read_sql(test_dataset, con=connect)
print(df_test)
multistep_df_test = window_input_output(3, df_test)
print(multistep_df_test)

# select the input features for the prediction
X_pred = multistep_df_test.drop(columns=['next_week_close_price'])

# use the trained model to make a prediction
prediction = model.predict(X_pred)

# print the prediction
print('Predicted stock price:', prediction)

