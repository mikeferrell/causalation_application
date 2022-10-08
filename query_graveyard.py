# #Mentions of inflation and comparing it to a stock (filtered in the where clause)
# query_results = f'''
# with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
# case when risk_factors ilike '%%inflat%%' then 1
# when risk_disclosures ilike '%%inflat%%' then 1
# else 0
# end as inflation_count
# from public.edgar_data
# where risk_factors != ''
# and risk_disclosures != ''
# order by inflation_count desc)
#
# select sum(inflation_count) as inflation_mentions, count(filing_url) as total_filings, DATE_TRUNC('month', filing_date) as filing_month
# from count_inflation_mentions
# group by filing_month
# order by filing_month asc
# ),
#
# stock_monthly_opening as (with temp_table as (
#                           select date(created_at) as created_at, close_price, stock_symbol
# from public.ticker_data
#     order
#
# by
# stock_symbol, date(created_at)
# asc
# )
#
# SELECT
# created_at,
# close_price,
# stock_symbol,
# LAG(created_at, 1)
# OVER(
#     ORDER
# BY
# stock_symbol, created_at
# ) as next_date,
#      case
# when
# split_part(LAG(created_at, 1)
# OVER(
#     ORDER
# BY
# stock_symbol, created_at
# )::TEXT, '-', 2) =
# split_part(created_at::TEXT, '-', 2) then
# null else created_at
# end as first_price_in_month
# FROM
# temp_table)
#
# select
# first_price_in_month as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
# from stock_monthly_opening join
#
# keyword_data
# on
# stock_monthly_opening.first_price_in_month = keyword_data.filing_month
# where
# stock_symbol in ('{stock_symbol}')```
# '''
#
# #frozen copy of dataframe_from_queries 10.7 when I decided to materialize queries
#     import pandas as pd
#     import passwords
#     from sqlalchemy import create_engine
#
#     url = passwords.rds_access
#
#     engine = create_engine(url)
#     connect = engine.connect()
#
#
#     def stock_symbol_dropdown(stock_symbol):
#         recent_prices = f'''select stock_symbol, close_price, date(created_at)
#         from ticker_data
#         where stock_symbol = '{stock_symbol}'
#         order by date(created_at) desc limit 30'''
#         recent_prices_df = pd.read_sql(recent_prices, con=connect)
#         return recent_prices_df
#
#
#     def keyword_dropdown():
#         keyword_count = f'''select distinct keywords, keyword_count from public.rake_data
#     order by keyword_count desc'''
#         keyword_count_df = pd.read_sql(keyword_count, con=connect)
#         keyword_count_df = keyword_count_df.iloc[:, 0]
#         return keyword_count_df
#
#
#     def keyword_table(keyword, start_date, end_date):
#         keyword_count = f'''with keyword_words as (SELECT
#                 date(filing_date) as filing_date,
#                   round(
#                     length(risk_factors) - length(REPLACE(risk_factors, '{keyword}', ''))
#                   ) / length('{keyword}') AS keyword_count
#                 FROM
#                   public.edgar_data
#                 WHERE filing_date >= '{start_date}'
#                 and filing_date <= '{end_date}'
#                 )
#
#                 select '{keyword}' as keywords,
#                 sum(keyword_count) as keyword_count
#                 from keyword_words
#                 where keyword_count > 0
#                 group by 1'''
#         keyword_count_df = pd.read_sql(keyword_count, con=connect)
#         return keyword_count_df
#
#
#     def stock_crypto_correlation_filtered(stock_symbol):
#         query_results = f'''
#                     with a as (
#                     with new_dates as (
#                     select coin_name,
#                     coin_price,
#                     date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#                     from public.crypto_data)
#
#                     select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price
#                     from ticker_data
#                     join new_dates on date(ticker_data.created_at)  + interval '1 month' = new_dates.close_date
#                     where created_at >= '2022-01-01'
#                     order by stock_symbol, created_at
#                     )
#
#                     select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
#                     from a
#                     where stock_symbol = '{stock_symbol}'
#                     group by 1, 2
#                     order by correlation desc
#                     limit 1
#                     '''
#         df_results = pd.read_sql(query_results, con=connect)
#         df_results = df_results.round({'correlation': 4})
#         return df_results
#
#
#     def change_stock_on_chart(stock_symbol):
#         query_results = f'''
#             with top_correlations as (with a as (
#             with new_dates as (
#             select coin_name,
#             coin_price,
#             date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#             from public.crypto_data)
#
#             select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price
#             from ticker_data
#             join new_dates on date(ticker_data.created_at) = new_dates.close_date
#             where created_at >= '2022-01-01'
#             order by stock_symbol, created_at
#             )
#
#             select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
#             from a
#             where stock_symbol = '{stock_symbol}'
#             group by 1, 2
#             order by correlation desc
#             limit 1)
#
#             select date(created_at) as created_at, close_price, stock_symbol,
#             coin_name,
#             coin_price,
#             date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#             from ticker_data join public.crypto_data on date(ticker_data.created_at) = date(split_part(crypto_data.close_date, '-', 3) || '-' || split_part(crypto_data.close_date, '-', 2) || '-' || split_part(crypto_data.close_date, '-', 1))
#             where stock_symbol in ('{stock_symbol}')
#             and coin_name in (select coin_name from top_correlations)
#             and date(created_at) >= '2022-01-01'
#             '''
#         df_results = pd.read_sql(query_results, con=connect)
#         return df_results
#
#
#     def inflation_mention_correlation(stock_symbol, start_date, end_date, filing_type, keyword, time_delay):
#         query_results = f'''
#                 with keyword_information as (with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
#             case when risk_factors ilike '%%{keyword}%%' then 1
#             when risk_disclosures ilike '%%{keyword}%%' then 1
#             else 0
#             end as inflation_count
#             from public.edgar_data
#             where risk_factors != ''
#             and risk_disclosures != ''
#             and filing_type = '{filing_type}'
#             order by inflation_count desc)
#
#             select sum(inflation_count) as inflation_mentions,
#             count(filing_url) as total_filings,
#             DATE_TRUNC('week',filing_date) as filing_week
#             from count_inflation_mentions
#             group by filing_week
#             order by filing_week asc
#             )
#             ,
#
#             stock_weekly_opening as (with temp_table as (
#             select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol
#             from public.ticker_data
#             order by stock_symbol, date(created_at)  asc
#             )
#
#             SELECT
#                 created_at,
#                 close_price,
#                 stock_symbol,
#                 LAG(created_at,1) OVER (
#                     ORDER BY stock_symbol, created_at
#                 ) as next_date,
#                     case when LAG(created_at) OVER (
#                     ORDER BY stock_symbol, created_at
#                 ) = created_at then null else created_at
#                 end as first_price_in_week
#             FROM
#                 temp_table)
#
#             select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as keyword_percentage
#             from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week + interval '{time_delay} week'
#             where first_price_in_week >= '{start_date}'
#             and first_price_in_week <= '{end_date}'
#             )
#
#
#             select stock_symbol, '{keyword} mentions' as "{keyword} Mentions", corr(close_price, keyword_percentage) * 1.000 as correlation
#             from keyword_information
#             where stock_symbol = '{stock_symbol}'
#             group by 1, 2
#             order by correlation desc
#             '''
#         df_results = pd.read_sql(query_results, con=connect)
#         df_results = df_results.round({'correlation': 4})
#         return df_results
#
#
#     def top_keyword_correlations_with_rolling_avg(asc_or_desc, keyword, start_date, end_date, time_delay):
#         query_results = f'''
#                 with top_correlations as (with rolling_average_calculation as (with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
#                 case when risk_factors ilike '%%{keyword}%%' then 1
#                 when risk_disclosures ilike '%%{keyword}%%' then 1
#                 else 0
#                 end as inflation_count
#                 from public.edgar_data
#                 where risk_factors != ''
#                 and risk_disclosures != ''
#                 order by inflation_count desc)
#
#                 select sum(inflation_count) as inflation_mentions,
#                 count(filing_url) as total_filings,
#                 DATE_TRUNC('week',filing_date) as filing_week
#                 from count_inflation_mentions
#                 group by filing_week
#                 order by filing_week asc
#                 )
#                 ,
#
#                 stock_weekly_opening as (with temp_table as (
#                 select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol
#                 from public.ticker_data
#                 order by stock_symbol, date(created_at)  asc
#                 )
#
#                 SELECT
#                     created_at,
#                     close_price,
#                     stock_symbol,
#                     LAG(created_at,1) OVER (
#                         ORDER BY stock_symbol, created_at
#                     ) as next_date,
#                         case when LAG(created_at) OVER (
#                         ORDER BY stock_symbol, created_at
#                     ) = created_at then null else created_at
#                     end as first_price_in_week
#                 FROM
#                     temp_table)
#
#                 select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
#                 from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week + interval '{time_delay} week'
#                 )
#
#                 select stock_date, stock_symbol,
#                 close_price,
#                 'Inflation Mentions' as inflation_mentions,
#                 avg(inflation_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as inflation_mentions_rolling_avg
#                 from rolling_average_calculation
#                 order by stock_symbol, stock_date
#                 )
#
#                 select stock_symbol as "Stock Symbol", '{keyword} Mentions' as "Keyword Mentions",
#                  corr(close_price, inflation_mentions_rolling_avg) * 1.000 as Correlation
#                 from top_correlations
#                 where stock_date >= '{start_date}'
#                 and stock_date <= '{end_date}'
#                 group by 1, 2
#                 order by Correlation {asc_or_desc}
#                 limit 10
#                     '''
#         df_results = pd.read_sql(query_results, con=connect)
#         df_results = df_results.round({'correlation': 4})
#         return df_results
#
#
#     # main chart. stock & keyword correlations. No time delay since it's a chart and not a correlation calculation
#     # all other fitlers work. Includes a 12 week rolling average
#     def inflation_mention_chart(stock_symbol, start_date, end_date, filing_type, keyword):
#         query_results = f'''
#             with rolling_average_calculation as (with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
#             case when risk_factors ilike '%%{keyword}%%' then 1
#             when risk_disclosures ilike '%%{keyword}%%' then 1
#             else 0
#             end as inflation_count
#             from public.edgar_data
#             where risk_factors != ''
#             and risk_disclosures != ''
#             and filing_type = '{filing_type}'
#             order by inflation_count desc)
#
#             select sum(inflation_count) as inflation_mentions,
#             count(filing_url) as total_filings,
#             DATE_TRUNC('week',filing_date) as filing_week
#             from count_inflation_mentions
#             group by filing_week
#             order by filing_week asc
#             )
#             ,
#
#             stock_weekly_opening as (with temp_table as (
#             select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol
#             from public.ticker_data
#             order by stock_symbol, date(created_at)  asc
#             )
#
#             SELECT
#                 created_at,
#                 close_price,
#                 stock_symbol,
#                 LAG(created_at,1) OVER (
#                     ORDER BY stock_symbol, created_at
#                 ) as next_date,
#                     case when LAG(created_at) OVER (
#                     ORDER BY stock_symbol, created_at
#                 ) = created_at then null else created_at
#                 end as first_price_in_week
#             FROM
#                 temp_table)
#
#             select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
#             from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week
#             )
#
#             select stock_date, stock_symbol,
#             close_price as stock_price,
#             '{keyword} Mentions' as "{keyword} Mentions",
#             avg(inflation_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as "{keyword} Mentions Rolling Average"
#             from rolling_average_calculation
#             where stock_symbol = '{stock_symbol}'
#             and stock_date >= '{start_date}'
#             and stock_date <= '{end_date}'
#             order by stock_symbol, stock_date
#             '''
#         query_results_df = pd.read_sql(query_results, con=connect)
#         query_results_df = query_results_df.round({f'{keyword} Mentions Rolling Average': 4})
#         return query_results_df
#
#
#     stock_dropdown_list_query = "select distinct stock_symbol from ticker_data order by stock_symbol asc"
#     average_close_price = "select stock_symbol, avg(close_price) as close_price from ticker_data group by 1"
#     correlation_query = '''
#     with a as (
#     with new_dates as (
#     select coin_name,
#     coin_price,
#     date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#     from public.crypto_data)
#
#     select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price
#     from ticker_data
#     join new_dates on date(ticker_data.created_at)  + interval '1 month' = new_dates.close_date
#     where created_at >= '2022-01-01'
#     order by stock_symbol, created_at
#     )
#
#     select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
#     from a
#     group by 1, 2
#     order by correlation desc
#     limit 100
#     '''
#     top_correlated_coin_and_stock = '''
#     with a as (
#     with new_dates as (
#     select coin_name,
#     coin_price,
#     date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#     from public.crypto_data)
#
#     select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price
#     from ticker_data
#     join new_dates on date(ticker_data.created_at)  + interval '1 month' = new_dates.close_date
#     where created_at >= '2022-01-01'
#     order by stock_symbol, created_at
#     )
#
#     select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
#     from a
#     group by 1, 2
#     order by correlation desc
#     limit 1
#     '''
#
#     top_stock_and_coin_close_prices_over_time = '''
#     with top_correlations as (with a as (
#     with new_dates as (
#     select coin_name,
#     coin_price,
#     date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#     from public.crypto_data)
#
#     select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price
#     from ticker_data
#     join new_dates on date(ticker_data.created_at) = new_dates.close_date
#     where created_at >= '2022-01-01'
#     order by stock_symbol, created_at
#     )
#
#     select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
#     from a
#     group by 1, 2
#     order by correlation desc
#     limit 1)
#
#     select date(created_at) as created_at, close_price, stock_symbol,
#     coin_name,
#     coin_price,
#     date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#     from ticker_data join public.crypto_data on date(ticker_data.created_at) = date(split_part(crypto_data.close_date, '-', 3) || '-' || split_part(crypto_data.close_date, '-', 2) || '-' || split_part(crypto_data.close_date, '-', 1))
#     where stock_symbol in (select stock_symbol from top_correlations)
#     and coin_name in (select coin_name from top_correlations)
#     and date(created_at) >= '2022-01-01'
#     '''
#
#     # output is pandas dataframe
#     ticker_data_frame = pd.read_sql(average_close_price, con=connect)
#     correlation_data_frame = pd.read_sql(correlation_query, con=connect)
#     stock_symbol_dropdown_list_df = pd.read_sql(stock_dropdown_list_query, con=connect)
#
#     stock_symbol_dropdown_list = stock_symbol_dropdown_list_df['stock_symbol'].tolist()
#
