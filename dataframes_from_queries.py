import pandas as pd
import passwords
from sqlalchemy import create_engine

url = passwords.rds_access

engine = create_engine(url)
connect = engine.connect()

average_close_price = "select stock_symbol, avg(close_price) as close_price from ticker_data group by 1"
correlation_query = '''
with a as (
with new_dates as (
select coin_name, 
coin_price,
date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
from public.crypto_data)

select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price 
from ticker_data
join new_dates on date(ticker_data.created_at)  + interval '1 month' = new_dates.close_date
where created_at >= '2022-01-01'
order by stock_symbol, created_at
)

select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
from a
group by 1, 2
order by correlation desc
limit 100
'''
top_correlated_coin_and_stock = '''
with a as (
with new_dates as (
select coin_name, 
coin_price,
date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
from public.crypto_data)

select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price 
from ticker_data
join new_dates on date(ticker_data.created_at)  + interval '1 month' = new_dates.close_date
where created_at >= '2022-01-01'
order by stock_symbol, created_at
)

select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
from a
group by 1, 2
order by correlation desc
limit 1
'''

top_stock_and_coin_close_prices_over_time = '''
with top_correlations as (with a as (
with new_dates as (
select coin_name, 
coin_price,
date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
from public.crypto_data)

select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price 
from ticker_data
join new_dates on date(ticker_data.created_at) = new_dates.close_date
where created_at >= '2022-01-01'
order by stock_symbol, created_at
)

select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
from a
group by 1, 2
order by correlation desc
limit 1)

select date(created_at) as created_at, close_price, stock_symbol,
coin_name, 
coin_price,
date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
from ticker_data join public.crypto_data on date(ticker_data.created_at) = date(split_part(crypto_data.close_date, '-', 3) || '-' || split_part(crypto_data.close_date, '-', 2) || '-' || split_part(crypto_data.close_date, '-', 1))
where stock_symbol in (select stock_symbol from top_correlations)
and coin_name in (select coin_name from top_correlations)
and date(created_at) >= '2022-01-01'
'''


#count the top 10 keywords. then, count all the keywords found in 'risk factors' grouped by filing date
#return filing date, keyword count
# select count(keywords) as keyword_count, filing_date from edgar_data where keywords in (select keyword_list) group by 2
# with keyword_list as (select count(keywords), keywords as keyword_count from rake_data group by 2 order by keyword_count desc limit 10)
# with keywords as (select risk_factors, keywords from edgar_data where risk_factors ilike (select keywords from keyword_list))

# def keyword_count_df():
#     keywords = "select count(keywords) as keyword_count, keywords from rake_data group by 2 order by keyword_count desc limit 10"
#     keywords_df = pd.read_sql(keywords, columns = ['keywords'], con=connect)
#     keywords_list = keywords_df.to_list()
#
#     keyword_query_results = []
#
#     for keyword in keywords_list:
#             keyword_count = f"""select filing date,
#                 round(length(risk_factors) - length(replace(risk_factors, "{keyword}", "")) / length"{keyword}") as keyword_count
#                 from edgar_data
#                 group by 1"""
#             sql_keywords_df = pd.read_sql(keyword_count, con=connect)
#             sql_keywords_list = sql_keywords_df.to_list()
#             keyword_query_results.append(sql_keywords_list)
#
#     return keyword_query_results

#this definition above won't work. try testing the above query with one keyword. If the query works, then
# need to figure out how to return it as a dataframe, then append that dataframe each time through the for loop


# output is pandas dataframe
ticker_data_frame = pd.read_sql(average_close_price, con=connect)
correlation_data_frame = pd.read_sql(correlation_query, con=connect)
# keyword_count_data_frame = keyword_count_df()
# top_correlated_coin_and_stock_data_frame = pd.read_sql(top_correlated_coin_and_stock, con=connect)
# top_stock_and_coin_close_prices_over_time_data_frame = pd.read_sql(top_stock_and_coin_close_prices_over_time, con=connect)

# print(top_stock_and_coin_close_prices_over_time_data_frame)