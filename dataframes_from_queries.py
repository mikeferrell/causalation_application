import pandas as pd
import passwords
from sqlalchemy import create_engine
from static.stock_list import stock_list

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


keyword_list = ['blockchain', 'cloud', 'covid', 'cryptocurrency',
                'currency exchange', 'election', 'exchange rate', 'growth', 'hack', 'housing market', 'inflation',
                'politic', 'profitability', 'recession', 'security', 'smartphone', 'supply chain', 'uncertainty', 'war']

#format percentages in query results
def format_percent(value):
    return "{:.0%}".format(value)

def format_dollar(value):
    return "${:.2f}".format(value)

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
    # stock_dropdown_list_query = 'select distinct stock_symbol from ticker_data order by stock_symbol asc'
    # stock_symbol_dropdown_list_df = pd.read_sql(stock_dropdown_list_query, con=connect)
    # stock_symbol_dropdown_list = stock_symbol_dropdown_list_df['stock_symbol'].tolist()
    stock_symbol_dropdown_list = stock_list
    return stock_symbol_dropdown_list

# def keyword_dropdown():
#     keyword_count = f'''select distinct keywords, keyword_count from public.rake_data
# order by keyword_count desc'''
#     keyword_count_df = pd.read_sql(keyword_count, con=connect)
#     keyword_count_df= keyword_count_df.iloc[:, 0]
#     return keyword_count_df

#get rid of this one and use the count from the other charts instead. this is just confusing things
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

def inflation_mention_correlation(stock_symbol, start_date, end_date, keyword, time_delay, filing_type):
    query_results = f'''
            with top_correlations as (with rolling_average_calculation as (
                 with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
                stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null)
            
                select 
                weekly_closing_price as stock_date
                , close_price
                , stock_symbol
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening 
                inner join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week + interval '{time_delay} week'
                where weekly_closing_price >= '{start_date}'
                and weekly_closing_price <= '{end_date}'
                and filing_type != '{filing_type}'
                )

                select stock_date, stock_symbol,
                close_price,
                'keyword Mentions' as keyword_mentions,
                avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, stock_date asc
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
    df_results['correlation'] = df_results['correlation'].apply(format_percent)
    return df_results


def top_keyword_correlations_with_rolling_avg(asc_or_desc, keyword, start_date, end_date, time_delay, filing_type):
    query_results = f'''
            with top_correlations as (with rolling_average_calculation as (
                 with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
                stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null)
            
                select 
                weekly_closing_price as stock_date
                , close_price
                , stock_symbol
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening 
                inner join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week + interval '{time_delay} week'
                where weekly_closing_price >= '{start_date}'
                and weekly_closing_price <= '{end_date}'
                and filing_type != '{filing_type}'
                )

                select stock_date, stock_symbol,
                close_price,
                '{keyword} Mentions' as keyword_mentions,
                avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, stock_date asc
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
    df_results['correlation'] = df_results['correlation'].apply(format_percent)
    return df_results

#main chart. stock & keyword correlations. No time delay since it's a chart and not a correlation calculations
#all other fitlers work. Includes a 12 week rolling average
def inflation_mention_chart(stock_symbol, start_date, end_date, keyword, limit, filing_type):
    query_results = f'''
            with rolling_average_calculation as (
                with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}')
                , stock_weekly_opening as (select * from weekly_stock_openings where weekly_closing_price is not null)
                
                select 
                distinct created_at as stock_date
                , close_price
                , stock_symbol
                , filing_type
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening 
                inner join keyword_data on stock_weekly_opening.created_at = keyword_data.filing_week
                where filing_type != '{filing_type}'
                )
            
            select stock_date, stock_symbol,
            close_price as stock_price,
            '{keyword} Mentions' as "{keyword} Mentions",
            avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as "{keyword} Mentions Rolling Average"
            from rolling_average_calculation
            where stock_symbol = '{stock_symbol}'
            and stock_date >= '{start_date}'
            and stock_date <= '{end_date}'
            order by stock_date asc
            offset 12
            {limit}
        '''
    query_results_df = pd.read_sql(query_results, con=connect)
    query_results_df = query_results_df.round({f'{keyword} Mentions Rolling Average': 4})
    query_results_df = query_results_df.round({'stock_price': 2})
    return query_results_df


def ml_accuracy_table():
    query_results = f'''
    with prices as (
    select current_week, current_close_price
    , stock_date as prediction_date, predicted_price as next_week_predicted_close, next_week_close_price
    , case when next_week_close_price > current_close_price then 'price increased'
        when next_week_close_price < current_close_price then 'price decreased'
        when next_week_close_price is null then 'no price comparison'
        else 'price the same'
        end as actual_price_movement
    , next_week_close_price - current_close_price as actual_price_change
    , (next_week_close_price / current_close_price) - 1 as actual_price_change_percentage
    , case when current_close_price < predicted_price then 'price increased'
        when current_close_price > predicted_price then 'price decreased'
        when predicted_price is null then 'no price comparison'
        else 'price the same'
        end as predicted_price_movement
    , predicted_price - current_close_price as predicted_price_change 
    , (current_close_price / predicted_price) - 1 as predicted_price_change_percentage 
    from prediction_results
    order by current_week asc
    )
    
    SELECT
    prediction_date 
    , actual_price_change
    , predicted_price_change
    , case when actual_price_movement = 'no price comparison' then 'no price comparison'
        when actual_price_movement = predicted_price_movement then 'correct prediction'
        else 'incorrect prediction'
        end as prediction_validation
    , case when actual_price_change = 0 then null else (actual_price_change - predicted_price_change) / current_close_price end as actual_prediction_percentage_delta
    from prices
    '''
    query_results_df = pd.read_sql(query_results, con=connect)
    query_results_df = query_results_df.round({'actual_price_change': 2})
    query_results_df = query_results_df.round({'predicted_price_change': 2})
    query_results_df = query_results_df.round({'actual_prediction_percentage_delta': 4})
    return query_results_df


def calculate_ml_model_accuracy():
    query_results_df = pd.DataFrame(columns=['stock_symbol', 'keyword', 'time_delay', 'filing_type', 'start_date',
                                             'current_week', 'prediction_date', 'current_close_price',
                                             'next_week_close_price', 'next_week_predicted_close',
                                             'actual_price_change',
                                             'predicted_price_change'])

    top_correlation_list = []

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
      and "Stock Symbol" not in ('GEHC', 'CAH')
      and "Keyword" != 'cryptocurrency Mentions'
    order by correlation desc
    limit 10
    '''
    df_of_top_ten_correlations = pd.read_sql(top_correlation_query_results, con=connect)

    row_range = range(0, 10)
    for rows in row_range:
        df_row = df_of_top_ten_correlations.iloc[rows]
        stock_symbol = df_row['stock_symbol']
        keyword = df_row['keyword']
        correlation_start_date = df_row['start_date']
        interval = df_row['time_delay']
        filing_type = df_row['filing_type']

        correlation_list = f'Stock Symbol: {stock_symbol}, Keyword: {keyword}, Start Date: {correlation_start_date}, ' \
                           f'Time Lag: {interval}, Filing Type: {filing_type}'
        top_correlation_list.append(correlation_list)

        query_results = f'''
                        with prices as (
                        select stock_symbol, start_date, keyword, time_delay, filing_type, current_week, current_close_price
                        , stock_date as prediction_date, predicted_price as next_week_predicted_close, next_week_close_price
                        , case when next_week_close_price > current_close_price then 'price increased'
                            when next_week_close_price < current_close_price then 'price decreased'
                            when next_week_close_price is null then 'no price comparison'
                            else 'price the same'
                            end as actual_price_movement
                        , next_week_close_price - current_close_price as actual_price_change
                        , (next_week_close_price / current_close_price) - 1 as actual_price_change_percentage
                        , case when current_close_price < predicted_price then 'price increased'
                            when current_close_price > predicted_price then 'price decreased'
                            when predicted_price is null then 'no price comparison'
                            else 'price the same'
                            end as predicted_price_movement
                        , predicted_price - current_close_price as predicted_price_change 
                        , (current_close_price / predicted_price) - 1 as predicted_price_change_percentage 
                        from top_five_prediction_results
                        where stock_symbol = '{stock_symbol}'
                        and keyword = '{keyword}'
                        and start_date = '{correlation_start_date}'
                        and time_delay = '{interval}'
                        and filing_type = '{filing_type}'
                        order by current_week asc
                        )

                        SELECT
                        stock_symbol, keyword, time_delay, filing_type, start_date, current_week, prediction_date, current_close_price, next_week_close_price, next_week_predicted_close
                        , actual_price_change
                        , predicted_price_change
                        , case when actual_price_movement = 'no price comparison' then 'no price comparison'
                            when actual_price_movement = predicted_price_movement then 'correct prediction'
                            else 'incorrect prediction'
                            end as prediction_validation
                        , actual_price_change - predicted_price_change as actual_prediction_delta
                        , case when actual_price_change = 0 then null else (actual_price_change - predicted_price_change) / current_close_price end as actual_prediction_percentage_delta
                        from prices
                        '''
        validationd_df = pd.read_sql(query_results, con=connect)
        df_full = pd.DataFrame(validationd_df)
        df_full['actual_prediction_percentage_delta'] = df_full['actual_prediction_percentage_delta'].apply(format_percent)
        df_full['current_close_price'] = df_full['current_close_price'].apply(format_dollar)
        df_full['next_week_close_price'] = df_full['next_week_close_price'].apply(format_dollar)
        df_full['next_week_predicted_close'] = df_full['next_week_predicted_close'].apply(format_dollar)
        df_full['actual_price_change'] = df_full['actual_price_change'].apply(format_dollar)
        df_full['predicted_price_change'] = df_full['predicted_price_change'].apply(format_dollar)
        df_full['actual_prediction_delta'] = df_full['actual_prediction_delta'].apply(format_dollar)
        df_full['start_date'] = pd.to_datetime(df_full['start_date']).apply(lambda x: x.date())
        df_full['current_week'] = pd.to_datetime(df_full['current_week'], format='%Y%m%d').apply(lambda x: x.date())
        df_full['prediction_date'] = pd.to_datetime(df_full['prediction_date']).apply(lambda x: x.date())
        query_results_df = query_results_df.append(df_full, ignore_index=True)
    return query_results_df, top_correlation_list, df_of_top_ten_correlations

# calculate_ml_model_accuracy()