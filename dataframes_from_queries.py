import pandas as pd
import passwords
from sqlalchemy import create_engine

url = passwords.rds_access

engine = create_engine(url)
connect = engine.connect()

keyword_list = ['blockchain', 'cloud', 'climate change', 'covid', 'cryptocurrency', 'currency exchange',
                'election', 'exchange rate', 'growth', 'hack', 'housing market', 'inflation', 'politic',
                'profitability', 'recession', 'security', 'smartphone', 'supply chain', 'uncertainty', 'war']

def close_prices(stock_symbol, start_date, end_date):
    recent_prices = f'''select stock_symbol, close_price, date(created_at) as close_date
    from ticker_data 
    where stock_symbol = '{stock_symbol}'
    and close_date >= '{start_date}'
    and close_date <= '{end_date}'
    order by date(created_at) desc 
    limit 30'''
    recent_prices_df = pd.read_sql(recent_prices, con=connect)
    return recent_prices_df

def stock_dropdown():
    stock_dropdown_list_query = 'select distinct stock_symbol from ticker_data order by stock_symbol asc'
    stock_symbol_dropdown_list_df = pd.read_sql(stock_dropdown_list_query, con=connect)
    stock_symbol_dropdown_list = stock_symbol_dropdown_list_df['stock_symbol'].tolist()
    return stock_symbol_dropdown_list

# def keyword_dropdown():
#     keyword_count = f'''select distinct keywords, keyword_count from public.rake_data
# order by keyword_count desc'''
#     keyword_count_df = pd.read_sql(keyword_count, con=connect)
#     keyword_count_df= keyword_count_df.iloc[:, 0]
#     return keyword_count_df

def keyword_table(keyword, start_date, end_date):
    keyword_count = f'''with keyword_words as (SELECT
            date(filing_date) as filing_date,
              round(
                length(risk_factors) - length(REPLACE(risk_factors, '{keyword}', ''))
              ) / length('{keyword}') AS keyword_count
            FROM
              public.edgar_data
            WHERE filing_date >= '{start_date}'
            and filing_date <= '{end_date}'
            )
              
            select '{keyword}' as keywords,
            sum(keyword_count) as keyword_count
            from keyword_words
            where keyword_count > 0
            group by 1'''
    keyword_count_df = pd.read_sql(keyword_count, con=connect)
    return keyword_count_df

#def stock_crypto_correlation_filtered(stock_symbol):
#     query_results = f'''
#                 with a as (
#                 with new_dates as (
#                 select coin_name,
#                 coin_price,
#                 date(split_part(close_date, '-', 3) || '-' || split_part(close_date, '-', 2) || '-' || split_part(close_date, '-', 1)) as close_date
#                 from public.crypto_data)
#
#                 select date(created_at) + interval '1 month' as created_at, close_price, stock_symbol, coin_name, coin_price
#                 from ticker_data
#                 join new_dates on date(ticker_data.created_at)  + interval '1 month' = new_dates.close_date
#                 where created_at >= '2022-01-01'
#                 order by stock_symbol, created_at
#                 )
#
#                 select stock_symbol, coin_name, corr(coin_price, close_price) * 1.000 as correlation
#                 from a
#                 where stock_symbol = '{stock_symbol}'
#                 group by 1, 2
#                 order by correlation desc
#                 limit 1
#                 '''
#     df_results = pd.read_sql(query_results, con=connect)
#     df_results = df_results.round({'correlation': 4})
#     return df_results

def inflation_mention_correlation(stock_symbol, start_date, end_date, keyword, time_delay):
    query_results = f'''
            with top_correlations as (with rolling_average_calculation as (
                 with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
                stock_weekly_opening as (select * from weekly_stock_openings)
            
                select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week + interval '{time_delay} week'
                where first_price_in_week >= '{start_date}'
                and first_price_in_week <= '{end_date}'
                )

                select stock_date, stock_symbol,
                close_price,
                'keyword Mentions' as keyword_mentions,
                avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, stock_date
                )
            
            select stock_symbol as "Stock Symbol", '{keyword} Mentions' as "Keyword Mentions",
             corr(close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
            from top_correlations
            where stock_date >= '{start_date}'
            and stock_date <= '{end_date}'
            and stock_symbol = '{stock_symbol}'
            group by 1, 2
        '''
    df_results = pd.read_sql(query_results, con=connect)
    df_results = df_results.round({'correlation': 4})
    return df_results


def top_keyword_correlations_with_rolling_avg(asc_or_desc, keyword, start_date, end_date, time_delay):
    query_results = f'''
            with top_correlations as (with rolling_average_calculation as (
                 with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
                stock_weekly_opening as (select * from weekly_stock_openings)
            
                select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week + interval '{time_delay} week'
                where first_price_in_week >= '{start_date}'
                and first_price_in_week <= '{end_date}'
                )

                select stock_date, stock_symbol,
                close_price,
                'keyword Mentions' as keyword_mentions,
                avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, stock_date
                )
            
            select stock_symbol as "Stock Symbol", '{keyword} Mentions' as "Keyword Mentions",
             corr(close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
            from top_correlations
            where stock_date >= '{start_date}'
            and stock_date <= '{end_date}'
            group by 1, 2
            order by Correlation {asc_or_desc}
            limit 10
                '''
    df_results = pd.read_sql(query_results, con=connect)
    df_results = df_results.round({'correlation': 4})
    return df_results

#main chart. stock & keyword correlations. No time delay since it's a chart and not a correlation calculations
#all other fitlers work. Includes a 12 week rolling average
def inflation_mention_chart(stock_symbol, start_date, end_date, keyword, limit):
    query_results = f'''
        with rolling_average_calculation as (
            with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
            stock_weekly_opening as (select * from weekly_stock_openings)
        
            select first_price_in_week as stock_date, close_price, stock_symbol, 1.00 * keyword_mentions / total_filings as keyword_percentage
            from stock_weekly_opening join keyword_data on stock_weekly_opening.first_price_in_week = keyword_data.filing_week
            )
        
        select stock_date, stock_symbol,
        close_price as stock_price,
        '{keyword} Mentions' as "{keyword} Mentions",
        avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as "{keyword} Mentions Rolling Average"
        from rolling_average_calculation
        where stock_symbol = '{stock_symbol}'
        and stock_date >= '{start_date}'
        and stock_date <= '{end_date}'
        order by stock_symbol, stock_date
        {limit}
        '''
    query_results_df = pd.read_sql(query_results, con=connect)
    query_results_df = query_results_df.round({f'{keyword} Mentions Rolling Average': 4})
    query_results_df = query_results_df.round({'stock_price': 2})
    return query_results_df



