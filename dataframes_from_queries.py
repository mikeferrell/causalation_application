import pandas as pd

import dataframes_from_queries
import passwords
from sqlalchemy import create_engine

url = passwords.rds_access

engine = create_engine(url)
connect = engine.connect()

def dropdown_results(stock_symbol):
    recent_prices = f'''select stock_symbol, close_price, date(created_at) 
    from ticker_data where stock_symbol = '{stock_symbol}'
    order by date(created_at) desc limit 30'''
    recent_prices_df = pd.read_sql(recent_prices, con=connect)
    return recent_prices_df

def stock_crypto_correlation_filtered(stock_symbol):
    query_results = f'''
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
                where stock_symbol = '{stock_symbol}'
                group by 1, 2
                order by correlation desc
                limit 1
                '''
    df_results = pd.read_sql(query_results, con=connect)
    return df_results


def change_stock_on_chart(stock_symbol):
    query_results = f'''
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
        where stock_symbol = '{stock_symbol}'
        group by 1, 2
        order by correlation desc
        limit 1)
        
        select date(created_at) as created_at, close_price, stock_symbol,
        coin_name, 
        coin_price,
        date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
        from ticker_data join public.crypto_data on date(ticker_data.created_at) = date(split_part(crypto_data.close_date, '-', 3) || '-' || split_part(crypto_data.close_date, '-', 2) || '-' || split_part(crypto_data.close_date, '-', 1))
        where stock_symbol in ('{stock_symbol}')
        and coin_name in (select coin_name from top_correlations)
        and date(created_at) >= '2022-01-01'
        '''
    df_results = pd.read_sql(query_results, con=connect)
    return df_results

def inflation_mention_correlation(stock_symbol):
    query_results = f'''with inflation_information as (with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
        case when risk_factors ilike '%%inflat%%' then 1
        when risk_disclosures ilike '%%inflat%%' then 1
        else 0 
        end as inflation_count
        from public.edgar_data 
        where risk_factors != ''
        and risk_disclosures != ''
        order by inflation_count desc)
        
        select sum(inflation_count) as inflation_mentions, count(filing_url) as total_filings, DATE_TRUNC('month',filing_date) as filing_month
        from count_inflation_mentions
        group by filing_month
        order by filing_month asc
        ),
        
        stock_monthly_opening as (with temp_table as (
        select date(created_at) as created_at, close_price, stock_symbol
        from public.ticker_data
        order by stock_symbol, date(created_at)  asc
        )
        
        SELECT
            created_at, 
            close_price,
            stock_symbol,
            LAG(created_at,1) OVER (
                ORDER BY stock_symbol, created_at
            ) as next_date,
                case when split_part(LAG(created_at,1) OVER (
                ORDER BY stock_symbol, created_at
            )::TEXT, '-', 2) = 
        split_part(created_at::TEXT, '-', 2) then null else created_at
            end as first_price_in_month
        FROM
            temp_table)
        
        select first_price_in_month as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
        from stock_monthly_opening join keyword_data on stock_monthly_opening.first_price_in_month = keyword_data.filing_month  + interval '1 month'
        )
        
        select stock_symbol, 'inflation mentions' as inflation_mentions, corr(close_price, inflation_percentage) * 1.000 as correlation
        from inflation_information
        where stock_symbol = '{stock_symbol}'
        group by 1, 2
        order by correlation desc
        '''
    df_results = pd.read_sql(query_results, con=connect)
    return df_results


def top_inflation_correlations_with_rolling_avg(asc_or_desc):
    query_results = f'''
            with top_correlations as (with rolling_average_calculation as (with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
            case when risk_factors ilike '%%inflat%%' then 1
            when risk_disclosures ilike '%%inflat%%' then 1
            else 0 
            end as inflation_count
            from public.edgar_data 
            where risk_factors != ''
            and risk_disclosures != ''
            order by inflation_count desc)
            
            select sum(inflation_count) as inflation_mentions, 
            count(filing_url) as total_filings, 
            DATE_TRUNC('week',filing_date) as filing_week
            from count_inflation_mentions
            group by filing_week
            order by filing_week asc
            )
            ,
            
            stock_weekly_opening as (with temp_table as (
            select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol
            from public.ticker_data
            order by stock_symbol, date(created_at)  asc
            )
            
            SELECT
                created_at, 
                close_price,
                stock_symbol,
                LAG(created_at,1) OVER (
                    ORDER BY stock_symbol, created_at
                ) as next_date,
                    case when LAG(created_at) OVER (
                    ORDER BY stock_symbol, created_at
                ) = created_at then null else created_at
                end as first_price_in_week
            FROM
                temp_table)
            
            select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
            from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week
            )
            
            select stock_date, stock_symbol,
            close_price,
            'Inflation Mentions' as inflation_mentions,
            avg(inflation_percentage) over(order by stock_symbol, stock_date rows 10 preceding) as inflation_mentions_rolling_avg
            from rolling_average_calculation
            order by stock_symbol, stock_date
            )
            
            select stock_symbol, inflation_mentions, corr(close_price, inflation_mentions_rolling_avg) * 1.000 as correlation
            from top_correlations
            where stock_date >= '2017-03-06'
            group by 1, 2
            order by correlation {asc_or_desc}
            limit 10
                '''
    df_results = pd.read_sql(query_results, con=connect)
    return df_results


def inflation_mention_chart(stock_symbol):
    query_results = f'''
        with rolling_average_calculation as (with keyword_data as (with count_inflation_mentions as (select date(filing_date) as filing_date, filing_url,
        case when risk_factors ilike '%%inflat%%' then 1
        when risk_disclosures ilike '%%inflat%%' then 1
        else 0 
        end as inflation_count
        from public.edgar_data 
        where risk_factors != ''
        and risk_disclosures != ''
        order by inflation_count desc)
        
        select sum(inflation_count) as inflation_mentions, 
        count(filing_url) as total_filings, 
        DATE_TRUNC('week',filing_date) as filing_week
        from count_inflation_mentions
        group by filing_week
        order by filing_week asc
        )
        ,
        
        stock_weekly_opening as (with temp_table as (
        select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol
        from public.ticker_data
        order by stock_symbol, date(created_at)  asc
        )
        
        SELECT
            created_at, 
            close_price,
            stock_symbol,
            LAG(created_at,1) OVER (
                ORDER BY stock_symbol, created_at
            ) as next_date,
                case when LAG(created_at) OVER (
                ORDER BY stock_symbol, created_at
            ) = created_at then null else created_at
            end as first_price_in_week
        FROM
            temp_table)
        
        select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * inflation_mentions / total_filings as inflation_percentage
        from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week
        )
        
        select stock_date, stock_symbol,
        avg(close_price) close_price as stock_price,
        'Inflation Mentions' as inflation_mentions,
        avg(inflation_percentage) over(order by stock_symbol, stock_date rows 25 preceding) as inflation_mentions_rolling_avg
        from rolling_average_calculation
        where stock_symbol = '{stock_symbol}'
        order by stock_symbol, stock_date
        '''
    query_results_df = pd.read_sql(query_results, con=connect)
    return query_results_df


stock_dropdown_list_query = "select distinct stock_symbol from ticker_data order by stock_symbol asc"
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
dropdown_list_df = pd.read_sql(stock_dropdown_list_query, con=connect)


dropdown_list = dropdown_list_df['stock_symbol'].tolist()
# keyword_count_data_frame = keyword_count_df()
# top_correlated_coin_and_stock_data_frame = pd.read_sql(top_correlated_coin_and_stock, con=connect)
# top_stock_and_coin_close_prices_over_time_data_frame = pd.read_sql(top_stock_and_coin_close_prices_over_time, con=connect)

