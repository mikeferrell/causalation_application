import pandas as pd
import passwords
from sqlalchemy import create_engine
from static.stock_list import stock_list
import ml_models.forecast_top_stocks_model_v2 as forecast_top_stocks_model
from datetime import date, timedelta

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


keyword_list = ['advertising', 'cloud', 'COVID', 'credit', 'currency exchange',
                'digital', 'election', 'exchange rate', 'growth', 'housing market', 'inflation',
                'insurance', 'politic', 'profitability', 'recession',
                'security', 'software', 'supply chain', 'uncertainty', 'war']

def get_dates():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    year = int(yesterdays_date[0:4])
    month = int(yesterdays_date[5:7])
    day = int(yesterdays_date[8:10])

    yesterday = str(date(year, month, day))
    return yesterday


#format percentages in query results
def format_percent(value):
    return "{:.0%}".format(value)


def format_dollar(value):
    return "${:,.2f}".format(value)


def format_rounded_dollar(value):
    return "${:,.0f}".format(value)

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

def sector_list():
    sector_query = f'''select distinct sector
    from ticker_sectors
    order by sector asc'''
    sector_list = pd.read_sql(sector_query, con=connect)
    sector_list = sector_list['sector'].tolist()
    return sector_list

def stock_dropdown_for_price_drops():
    query = f'''select distinct on (ticker_data.stock_symbol) ticker_data.stock_symbol, company_name
    from ticker_data
    inner join stock_names on ticker_data.stock_symbol = stock_names.stock_symbol
    where ticker_data.stock_symbol not in ('^GSPC', '^SP500TR')

    union all

    select distinct on (ticker_data_russell.stock_symbol) ticker_data_russell.stock_symbol, company_name
    from ticker_data_russell
    inner join stock_names on ticker_data_russell.stock_symbol = stock_names.stock_symbol
    where ticker_data_russell.stock_symbol not in ('^GSPC', '^SP500TR')
    '''
    query_df = pd.read_sql(query, con=connect)
    query_df = query_df.sort_values(by=['stock_symbol'], ascending=True)
    stock_symbols = query_df['stock_symbol'].tolist()
    company_names = query_df['company_name'].tolist()
    return stock_symbols, company_names



def stock_dropdown():
    # stock_dropdown_list_query = 'select distinct stock_symbol from ticker_data order by stock_symbol asc'
    # stock_symbol_dropdown_list_df = pd.read_sql(stock_dropdown_list_query, con=connect)
    # stock_symbol_dropdown_list = stock_symbol_dropdown_list_df['stock_symbol'].tolist()
    stock_symbol_dropdown_list = stock_list
    return stock_symbol_dropdown_list


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
    keyword_count_df = keyword_count_df.rename(columns={'keywords':'Keywords', 'keyword_count':'Keyword Count'})
    return keyword_count_df


def inflation_mention_correlation(stock_symbol, start_date, end_date, keyword, time_delay, filing_type):
    query_results = f'''
            with top_correlations as (with rolling_average_calculation as (
                 with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
                stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null)
            
                select 
                week_opening_date
                , week_close_price
                , stock_symbol
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening 
                inner join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week + interval '{time_delay} week'
                where week_opening_date >= '{start_date}'
                and week_opening_date <= '{end_date}'
                and filing_type != '{filing_type}'
                )

                select week_opening_date, stock_symbol,
                week_close_price,
                'keyword Mentions' as keyword_mentions,
                avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, week_opening_date asc
                offset 6
                )
            
            select stock_symbol as "Stock Symbol", '{keyword} Mentions' as "Keyword Mentions",
             corr(week_close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
            from top_correlations
            where week_opening_date >= '{start_date}'
            and week_opening_date <= '{end_date}'
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
                stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null)
            
                select 
                week_opening_date
                , week_close_price
                , stock_symbol
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening 
                inner join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week + interval '{time_delay} week'
                where week_opening_date >= '{start_date}'
                and week_opening_date <= '{end_date}'
                and filing_type != '{filing_type}'
                )

                select week_opening_date, stock_symbol,
                week_close_price,
                '{keyword} Mentions' as keyword_mentions,
                avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                from rolling_average_calculation
                order by stock_symbol, week_opening_date asc
                offset 6
                )
            
            select stock_symbol as "Stock Symbol", '{keyword} Mentions' as "Keyword Mentions",
             corr(week_close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
            from top_correlations
            where week_opening_date >= '{start_date}'
            and week_opening_date <= '{end_date}'
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
                , stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null)
                
                select 
                distinct week_opening_date
                , week_close_price
                , stock_symbol
                , filing_type
                , 1.00 * keyword_mentions / total_filings as keyword_percentage
                from stock_weekly_opening 
                inner join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week
                where filing_type != '{filing_type}'
                )
            
            select week_opening_date, stock_symbol,
            week_close_price,
            '{keyword} Mentions' as "{keyword} Mentions",
            avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as "{keyword} Mentions Rolling Average"
            from rolling_average_calculation
            where stock_symbol = '{stock_symbol}'
            and week_opening_date >= '{start_date}'
            and week_opening_date <= '{end_date}'
            order by week_opening_date asc
            offset 6
            {limit}
        '''
    query_results_df = pd.read_sql(query_results, con=connect)
    query_results_df = query_results_df.round({f'{keyword} Mentions Rolling Average': 4})
    query_results_df = query_results_df.round({'week_close_price': 2})

    #ROI for the stock
    starting_price_stock = query_results_df['week_close_price'].values[:1]
    ending_price_stock = query_results_df['week_close_price'].values[-1:]
    starting_price_stock = starting_price_stock[0]
    ending_price_stock = ending_price_stock[0]
    stock_returns = (ending_price_stock - starting_price_stock) / starting_price_stock
    stock_returns = "{:.1%}".format(stock_returns)
    return query_results_df, stock_returns

# query, stocks = inflation_mention_chart('ETSY', '2021-01-01', '2022-01-01', 'cloud', ' ', '10-Q')
# print(query, stocks)

def ml_accuracy_table():
    query_results = f'''
    with prices as (
    select current_week, current_close_price
    , week_opening_date as prediction_date, predicted_price as next_week_predicted_close, next_week_close_price
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


def daily_top_ten_correlations():
    query_df = f'''select * from top_ten_correlations_today'''
    query_df = pd.read_sql(query_df, con=connect)
    return query_df


def stocks_to_buy_this_week(principal, this_week_or_last_table):
    if this_week_or_last_table == 'future_buy_recommendations':
        buy_date = '''previous_weekly_open_date + interval '7' day'''
    else:
        buy_date = 'previous_weekly_open_date'

    query_results = f'''
            with buy_recs as (  
              select {buy_date} as buy_date
              , previous_weekly_close_price
              , predicted_weekly_close_price
              , (predicted_weekly_close_price / previous_weekly_close_price) - 1 as predicted_growth
              , stock_symbol 
              , keyword
              from {this_week_or_last_table}
              where predicted_weekly_close_price > previous_weekly_close_price
              and previous_weekly_open_date >= date('{get_dates()}') - interval '9' day
              and keyword != 'hack'
              and stock_symbol not in ('SBNY')
              and ((predicted_weekly_close_price / previous_weekly_close_price) - 1) > 0.05
              ),
              
            buy_amounts as (
              with stock_selections as (
              SELECT
                  stock_symbol,
                  previous_weekly_open_date,
                  previous_weekly_close_price,
                  predicted_weekly_close_price, 
                  (predicted_weekly_close_price / previous_weekly_close_price) - 1 AS predicted_price_change_percentage
              FROM
                  public.{this_week_or_last_table}
              WHERE predicted_weekly_close_price > previous_weekly_close_price
              and previous_weekly_open_date >= date('{get_dates()}') - interval '9' day
              and keyword != 'hack'
              and stock_symbol not in ('SBNY')
              and ((predicted_weekly_close_price / previous_weekly_close_price) - 1) > 0.05
            ),
            
            total_estimation as (
              select previous_weekly_open_date, sum(predicted_price_change_percentage) as total_change_amount
              from stock_selections
              group by previous_weekly_open_date
            )
            
            select 
              stock_symbol
              , previous_weekly_close_price
              , {principal} as principal_amount
              , ({principal} * (predicted_price_change_percentage / total_change_amount)) / previous_weekly_close_price as number_of_shares_to_purchase
              , predicted_price_change_percentage / total_change_amount as scaled_predicted_change
            from 
              stock_selections 
              join total_estimation on stock_selections.previous_weekly_open_date = total_estimation.previous_weekly_open_date
            where predicted_price_change_percentage != 0
            order by 
             stock_symbol asc
            )
            
            select buy_date
            , buy_recs.stock_symbol
            , buy_recs.keyword
            , buy_recs.previous_weekly_close_price
            , buy_recs.predicted_weekly_close_price
            , predicted_growth
            , number_of_shares_to_purchase
            , principal_amount
            from buy_recs join buy_amounts on buy_recs.stock_symbol = buy_amounts.stock_symbol
                    '''
    buys_df = pd.read_sql(query_results, con=connect)
    df_full = pd.DataFrame(buys_df)
    df_full['buy_date'] = pd.to_datetime(df_full['buy_date']).apply(lambda x: x.date())
    df_full['predicted_weekly_close_price'] = df_full['predicted_weekly_close_price'].apply(format_dollar)
    df_full['predicted_growth'] = df_full['predicted_growth'].apply(format_percent)
    df_full['previous_weekly_close_price'] = df_full['previous_weekly_close_price'].apply(format_dollar)
    df_full['principal_amount'] = df_full['principal_amount'].apply(format_dollar)
    df_full = df_full.round({'number_of_shares_to_purchase': 2})
    df_full.rename(columns={'buy_date': 'Buy Date',
                            'stock_symbol': 'Stock Symbol',
                            'keyword': 'Correlated Keyword',
                             'predicted_weekly_close_price': 'Predicted Weekly Close Price',
                             'previous_weekly_close_price': 'Previous Week Close Price',
                            'predicted_growth': 'Predicted Growth',
                            'principal_amount': 'Principal Amount',
                            'number_of_shares_to_purchase': 'Number of Shares to Purchase'
                            }, inplace=True)

    #pull data from last week to determine the returns
    if this_week_or_last_table == 'last_week_buy_recommendations':
        close_data_query = f'''
          select stock_symbol, week_opening_date, week_open_price, week_close_price from public.weekly_stock_openings
            where week_opening_date >= date('{forecast_top_stocks_model.defined_dates()[0]}') - interval '14' day
            '''
        query_df = pd.read_sql(close_data_query, con=connect)
        formatted_df = pd.DataFrame(query_df)
        formatted_df['week_opening_date'] = pd.to_datetime(formatted_df['week_opening_date']).apply(lambda x: x.date())
        merged_df = pd.merge(formatted_df, df_full, left_on=['stock_symbol', 'week_opening_date'], 
                             right_on=['Stock Symbol', 'Buy Date'])
        merged_df = merged_df.drop(columns=['Predicted Growth', 'Buy Date', 'Stock Symbol', 'Predicted Weekly Close Price',
                                            'Previous Week Close Price'])

        #calculate returns from last week
        returns_for_date = ((merged_df['week_close_price'] * merged_df[
            'Number of Shares to Purchase'])
                            - (merged_df['week_open_price'] * merged_df[
                    'Number of Shares to Purchase'])).sum()
        cash_in_hand = principal + returns_for_date
        end_of_week_performance = '{:.2%}'.format((cash_in_hand / principal) - 1)
    else:
        end_of_week_performance = 1

    return df_full, end_of_week_performance

# df_full, end_of_week_performance = stocks_to_buy_this_week(1000, 'last_week_buy_recommendations')
# print(end_of_week_performance)

def buy_date():
    query_results = f'''
                    select previous_weekly_open_date + interval '7' day as buy_date
                    from future_buy_recommendations
                    limit 1
                    '''
    buys_df = pd.read_sql(query_results, con=connect)
    df_full = pd.DataFrame(buys_df)
    df_full['buy_date'] = pd.to_datetime(df_full['buy_date']).apply(lambda x: x.date())
    return df_full

def s_and_p_returns_for_daterange(start_date, end_date):
    sandp_query = f'''
    select created_at as week_of_purchases, close_price as s_and_p_price from ticker_data
    where stock_symbol = '^GSPC'
    and created_at >= '{start_date}'
    and created_at <= '{end_date}'
    order by created_at asc
    '''
    sandp_df = pd.read_sql(sandp_query, con=connect)

    starting_price_sp = sandp_df['s_and_p_price'].values[:1]
    ending_price_sp = sandp_df['s_and_p_price'].values[-1:]
    starting_price_sp = starting_price_sp[0]
    ending_price_sp = ending_price_sp[0]
    s_and_p_returns = (ending_price_sp - starting_price_sp) / starting_price_sp
    s_and_p_returns = "{:.1%}".format(s_and_p_returns)
    return s_and_p_returns


#calculating the % of times that SEC average counts move in the same direct time_delay weeks before stocks move the same
#direction
def stock_moving_with_sec_data(stock_symbol, start_date, end_date, keyword, time_delay, filing_type):
    query_results = f'''
    with weekly_data as (
    with rolling_average_calculation as (
         with keyword_data as (select * from keyword_weekly_counts where keyword = '{keyword}'),
        stock_weekly_opening as (select * from weekly_stock_openings where week_opening_date is not null)
    
        select 
        week_opening_date
        , LAG(week_opening_date, {time_delay}) OVER (
          ORDER BY stock_symbol, week_opening_date
        ) as last_week_opening_date
        , week_close_price
        , stock_symbol
        , 1.00 * keyword_mentions / total_filings as keyword_percentage
        from stock_weekly_opening 
        inner join keyword_data on stock_weekly_opening.week_opening_date = keyword_data.filing_week + interval '{time_delay} week'
        where week_opening_date >= '{start_date}'
        and week_opening_date <= '{end_date}'
        and filing_type != '{filing_type}'
        and stock_symbol = '{stock_symbol}'
        offset 6
        )
    
        select week_opening_date
        , last_week_opening_date
        , stock_symbol
        , week_close_price
        , avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
        from rolling_average_calculation
        order by stock_symbol, week_opening_date asc
    )
    
    select dateweek.week_opening_date, dateweek.week_close_price, prevweek.keyword_mentions_rolling_avg
    , case when dateweek.week_close_price > prevweek.week_close_price then 'moved_up'
      when dateweek.week_close_price < prevweek.week_close_price then 'moved_down'
      when dateweek.week_close_price = prevweek.week_close_price then 'no_move'
      end as stock_moves
    , case when dateweek.keyword_mentions_rolling_avg > prevweek.keyword_mentions_rolling_avg then 'moved_up'
      when dateweek.keyword_mentions_rolling_avg < prevweek.keyword_mentions_rolling_avg then 'moved_down'
      when dateweek.keyword_mentions_rolling_avg = prevweek.keyword_mentions_rolling_avg then 'no_move'
      end as keyword_moves
    from weekly_data as prevweek
    join weekly_data as dateweek on prevweek.week_opening_date = dateweek.last_week_opening_date 
    '''
    query_df = pd.read_sql(query_results, con=connect)
    row_count = len(query_df)
    same_moves = len(query_df.query('stock_moves == keyword_moves'))
    sec_and_stock_move_together = (same_moves / row_count)
    sec_and_stock_move_together = "{:.1%}".format(sec_and_stock_move_together)
    return sec_and_stock_move_together

# stock_moving_with_sec_data('ETSY', '2021-01-01', "2022-02-02", 'cloud', '2', '10-Q')

##                                          ##
## Calculations for finding undervalued Stocks
##                                          ##

def biggest_price_drop(stock_dropdown, company_dropdown, sector_dropdown, start_date, end_date, order_by, order_by_order,
                       numeric_input_low, numeric_input_high):
    if stock_dropdown == '':
        stock_symbol_s_and_p = ''
        stock_symbol_russell = ''
    else:
        stock_symbol_s_and_p = f'''and ticker_data.stock_symbol = '{stock_dropdown}' '''
        stock_symbol_russell = f'''and ticker_data_russell.stock_symbol = '{stock_dropdown}' '''
    if company_dropdown == '':
        company_dropdown = ''
    else:
        company_dropdown = f'''and company_name = '{company_dropdown}' '''
    if sector_dropdown == '':
        sector = ''
    else:
        sector = f'''and sector = '{sector_dropdown}' '''
    if order_by == '':
        order_by = 'Price Change'
    else:
        order_by = order_by
    if order_by_order == 'Ascending':
        order_by_order = True
    elif order_by_order == '':
        order_by_order = True
    else:
        order_by_order = False


    query_df = f'''select company_name, ticker_data.stock_symbol, created_at, close_price, sector as Sector,
            ((most_recent_total_assets::DECIMAL) / (peak_price_total_assets::DECIMAL)) - 1 as asset_growth_since_peak
            , ((most_recent_total_cash_and_equivelants::DECIMAL) / (peak_price_total_cash_and_equivelants::DECIMAL)) - 1 as cash_growth_since_peak
            from ticker_data join ticker_sectors on ticker_data.stock_symbol = ticker_sectors.stock_symbol
            join ticker_balance_sheet_data on ticker_data.stock_symbol = ticker_balance_sheet_data.stock_symbol
            join stock_names on ticker_data.stock_symbol = stock_names.stock_symbol
            where created_at >= '{start_date}'
            and created_at <= '{end_date}'
            {stock_symbol_s_and_p}
            {sector}
            {company_dropdown}
            
            union all
        
            select company_name, ticker_data_russell.stock_symbol, created_at, close_price, sector as Sector,
            ((most_recent_total_assets::DECIMAL) / (peak_price_total_assets::DECIMAL)) - 1 as asset_growth_since_peak
            , ((most_recent_total_cash_and_equivelants::DECIMAL) / (peak_price_total_cash_and_equivelants::DECIMAL)) - 1 as cash_growth_since_peak
            from ticker_data_russell join ticker_sectors_russell on ticker_data_russell.stock_symbol = ticker_sectors_russell.stock_symbol
            join public.ticker_balance_sheet_data_russell on ticker_data_russell.stock_symbol = ticker_balance_sheet_data_russell.stock_symbol
            join stock_names on ticker_data_russell.stock_symbol = stock_names.stock_symbol
            where created_at >= '{start_date}'
            and created_at <= '{end_date}'
            {stock_symbol_russell}
            {sector}
            {company_dropdown}
            '''

    df_results = pd.read_sql(query_df, con=connect)
    highest_price = df_results.loc[df_results.groupby('stock_symbol')['close_price'].idxmax()]
    most_recent_price = df_results.loc[df_results.groupby('stock_symbol')['created_at'].idxmax()]
    merged_df = pd.merge(highest_price, most_recent_price, how='inner', on=['stock_symbol'])
    merged_df = merged_df.rename(columns={'close_price_x': 'highest_price', 'close_price_y': 'current_price',
                                          'created_at_x': 'highest_price_date', 'created_at_y': 'current_date',
                                          'sector_x': 'Sector', 'cash_growth_since_peak_x': 'cash_growth_since_peak',
                                          'asset_growth_since_peak_x': 'asset_growth_since_peak'})
    merged_df['price_change'] = (merged_df['current_price'] / merged_df['highest_price']) - 1
    merged_df['days_since_ath'] = merged_df['current_date'] - merged_df['highest_price_date']

    #Max company value
    company_value_query = f'''
        select stock_symbol,
        (peak_price_shares_outstanding::DECIMAL) as peak_price_shares_outstanding,
        (most_recent_shares_outstanding::DECIMAL) as most_recent_shares_outstanding
        from ticker_balance_sheet_data
        
        union all
        
        select stock_symbol,
        (peak_price_shares_outstanding::DECIMAL) as peak_price_shares_outstanding,
        (most_recent_shares_outstanding::DECIMAL) as most_recent_shares_outstanding
        from ticker_balance_sheet_data_russell
        '''
    company_value_df = pd.read_sql(company_value_query, con=connect)
    merged_company_value_df = pd.merge(merged_df, company_value_df, how='inner', on=['stock_symbol'])
    merged_company_value_df['max_company_value'] =\
        merged_company_value_df['highest_price'] * merged_company_value_df['peak_price_shares_outstanding']
    merged_company_value_df['most_recent_company_value'] =\
        merged_company_value_df['current_price'] * merged_company_value_df['most_recent_shares_outstanding']
    merged_company_value_df['company_value_change'] =\
        ((merged_company_value_df['current_price'] * merged_company_value_df['most_recent_shares_outstanding']) /
            (merged_company_value_df['highest_price'] * merged_company_value_df['peak_price_shares_outstanding'])) - 1

    #Earning to company value
    company_earnings_query = f'''
    select stock_symbol, 
    case when peak_price_ebitda = 'None' then 0 else (peak_price_ebitda::decimal) end as peak_price_ebitda,
    case when most_recent_ebitda = 'None' then 0 else (most_recent_ebitda::decimal) end as most_recent_ebitda
    from ticker_revenue_data
    
    union all
    
        select stock_symbol, 
    case when peak_price_ebitda = 'None' then 0 else (peak_price_ebitda::decimal) end as peak_price_ebitda,
    case when most_recent_ebitda = 'None' then 0 else (most_recent_ebitda::decimal) end as most_recent_ebitda
    from ticker_revenue_data_russell
    '''
    company_earnings_df = pd.read_sql(company_earnings_query, con=connect)
    merged_company_value_df = pd.merge(company_earnings_df, merged_company_value_df, how='inner', on=['stock_symbol'])

    #EBITDA
    merged_company_value_df['ebitda_change'] = (merged_company_value_df['most_recent_ebitda'] /
                                                merged_company_value_df['peak_price_ebitda']) - 1
    #P/S Ratio
    merged_company_value_df['peak_price_to_sale_ratio'] = \
        (merged_company_value_df['highest_price'] * merged_company_value_df['peak_price_shares_outstanding']) / \
        (merged_company_value_df['peak_price_ebitda'] * 4)
    merged_company_value_df['current_price_to_sale_ratio'] = \
        (merged_company_value_df['current_price'] * merged_company_value_df['most_recent_shares_outstanding']) / \
        (merged_company_value_df['most_recent_ebitda'] * 4)
    merged_company_value_df['p_s_ratio_change'] = (merged_company_value_df['current_price_to_sale_ratio'] /
                                                   merged_company_value_df['peak_price_to_sale_ratio']) - 1
    #EPS
    merged_company_value_df.loc[merged_company_value_df['peak_price_ebitda'] <= 0, 'peak_eps'] = 0
    merged_company_value_df.loc[merged_company_value_df['most_recent_ebitda'] <= 0, 'most_recent_eps'] = 0
    merged_company_value_df.loc[merged_company_value_df['peak_price_ebitda'] > 0, 'peak_eps'] = (
            merged_company_value_df['peak_price_ebitda'] / merged_company_value_df['peak_price_shares_outstanding'])
    merged_company_value_df.loc[merged_company_value_df['most_recent_ebitda'] > 0, 'most_recent_eps'] = (
            merged_company_value_df['most_recent_ebitda'] / merged_company_value_df['most_recent_shares_outstanding'])
    merged_company_value_df['eps_change'] = (merged_company_value_df['most_recent_eps'] /
                                             merged_company_value_df['peak_eps']) - 1

    #PE Ratio
    merged_company_value_df['peak_pe_ratio'] = merged_company_value_df['highest_price'] / merged_company_value_df['peak_eps']
    merged_company_value_df['most_recent_pe_ratio'] = merged_company_value_df['current_price'] / merged_company_value_df[
        'most_recent_eps']
    merged_company_value_df['pe_ratio_change'] = (merged_company_value_df['most_recent_pe_ratio'] /
                                                  merged_company_value_df['peak_pe_ratio']) - 1

    #format
    merged_company_value_df = merged_company_value_df.drop(
        columns=['sector_y', 'asset_growth_since_peak_y', 'cash_growth_since_peak_y', 'current_date',
                 'peak_price_shares_outstanding', 'most_recent_shares_outstanding', 'Sector'])
    merged_company_value_df = merged_company_value_df.rename(columns={'company_name_x': 'Company Name',
        'stock_symbol': 'Stock Symbol', 'price_change': 'Price Change', 'asset_growth_since_peak': 'Asset Growth Since Peak',
        'cash_growth_since_peak': 'Cash Growth Since Peak', 'current_price': 'Current Price',
        'highest_price': 'Highest Price', 'days_since_ath': 'Days Since Peak Price',
        'highest_price_date': 'Peak Price Date', 'max_company_value': 'Peak Company Value',
        'most_recent_company_value': 'Most Recent Company Value',
        'company_value_change': 'Company Value Change', 'peak_eps': 'EPS at Peak Price',
        'most_recent_eps': 'Most Recent EPS', 'eps_change': 'EPS Change',
        'peak_price_to_sale_ratio': 'Peak Price to Sales Ratio', 'current_price_to_sale_ratio': 'Most Recent Price to Sales Ratio',
        'p_s_ratio_change': 'Price to Sales Ratio Change', 'peak_pe_ratio': 'Peak P/E Ratio',
        'most_recent_pe_ratio': 'Most Recent P/E Ratio', 'pe_ratio_change': 'P/E Ratio Change', 'peak_price_ebitda': 'Peak Price EBITDA',
        'most_recent_ebitda': 'Most Recent EBITDA', 'ebitda_change': 'EBITDA Change'})
    new_column_order = ['Company Name', 'Stock Symbol', 'Price Change', 'Highest Price', 'Current Price', 'Days Since Peak Price',
                        'Peak Price Date', 'Cash Growth Since Peak', 'Asset Growth Since Peak',
                        'Company Value Change', 'Peak Company Value', 'Most Recent Company Value',
                        'EPS Change', 'EPS at Peak Price', 'Most Recent EPS',
                        'Price to Sales Ratio Change', 'Peak Price to Sales Ratio', 'Most Recent Price to Sales Ratio',
                        'P/E Ratio Change', 'Peak P/E Ratio', 'Most Recent P/E Ratio',
                        'EBITDA Change', 'Peak Price EBITDA', 'Most Recent EBITDA']
    merged_company_value_df = merged_company_value_df.reindex(columns=new_column_order)
    # print(merged_company_value_df)

    #order by and filter
    columns = [col for col in merged_company_value_df.columns if col not in ['Company Name', 'Sector', 'Stock Symbol',
                                                                             'Peak Price Date', 'Days Since Peak Price']]
    for column in columns:
        merged_company_value_df[column] = merged_company_value_df[column].astype(float)
    merged_company_value_df = merged_company_value_df.sort_values(by=[f'{order_by}'], ascending=order_by_order)
    merged_company_value_df = merged_company_value_df[(merged_company_value_df[f'{order_by}'] >= numeric_input_low) &
                                       (merged_company_value_df[f'{order_by}'] <= numeric_input_high)]


    #Financial Data
    merged_company_value_df['Price Change'] = merged_company_value_df['Price Change'].apply(lambda x: "{:.1%}".format(x))
    merged_company_value_df['Asset Growth Since Peak'] = merged_company_value_df['Asset Growth Since Peak'].apply(lambda x: "{:.1%}".format(x))
    merged_company_value_df['Cash Growth Since Peak'] = merged_company_value_df['Cash Growth Since Peak'].apply(lambda x: "{:.1%}".format(x))
    merged_company_value_df['Current Price'] = merged_company_value_df['Current Price'].apply(format_dollar)
    merged_company_value_df['Highest Price'] = merged_company_value_df['Highest Price'].apply(format_dollar)
    merged_company_value_df['Days Since Peak Price'] = pd.to_timedelta(merged_company_value_df['Days Since Peak Price'])
    merged_company_value_df['Days Since Peak Price'] = merged_company_value_df['Days Since Peak Price'].apply(lambda x: x.days)
    merged_company_value_df['Peak Price Date'] = merged_company_value_df['Peak Price Date'].apply(lambda x: x.date())
    merged_company_value_df['Peak Company Value'] = merged_company_value_df['Peak Company Value'].apply(format_rounded_dollar)
    merged_company_value_df['Most Recent Company Value'] = merged_company_value_df['Most Recent Company Value'].apply(format_rounded_dollar)
    merged_company_value_df['Company Value Change'] = merged_company_value_df['Company Value Change'].apply(lambda x: "{:.1%}".format(x))
    #EBITDA
    merged_company_value_df['Peak Price EBITDA'] = merged_company_value_df['Peak Price EBITDA'].apply(format_rounded_dollar)
    merged_company_value_df['Most Recent EBITDA'] = merged_company_value_df['Most Recent EBITDA'].apply(format_rounded_dollar)
    merged_company_value_df['EBITDA Change'] = merged_company_value_df['EBITDA Change'].apply(lambda x: "{:.1%}".format(x))
    #EPS
    merged_company_value_df['EPS at Peak Price'] = merged_company_value_df['EPS at Peak Price'].apply(format_dollar)
    merged_company_value_df['Most Recent EPS'] = merged_company_value_df['Most Recent EPS'].apply(format_dollar)
    merged_company_value_df['EPS Change'] = merged_company_value_df['EPS Change'].apply(lambda x: "{:.1%}".format(x))
    #P/S
    merged_company_value_df['Peak Price to Sales Ratio'] = round(merged_company_value_df['Peak Price to Sales Ratio'])
    merged_company_value_df['Most Recent Price to Sales Ratio'] = round(merged_company_value_df['Most Recent Price to Sales Ratio'])
    merged_company_value_df['Price to Sales Ratio Change'] = merged_company_value_df['Price to Sales Ratio Change'].apply(lambda x: "{:.1%}".format(x))
    #PE
    merged_company_value_df['Peak P/E Ratio'] = round(merged_company_value_df['Peak P/E Ratio'])
    merged_company_value_df['Most Recent P/E Ratio'] = round(merged_company_value_df['Most Recent P/E Ratio'])
    merged_company_value_df['P/E Ratio Change'] = merged_company_value_df['P/E Ratio Change'].apply(lambda x: "{:.1%}".format(x))

    return merged_company_value_df


#create revenue chart for price drop page
def revenue_data_from_json_column(stock_symbol):
    query_results = f'''with a as (
    SELECT (json_each(cast(ebitda_last_5_years as json))).key AS "Reporting Date", 
    (json_each(cast(ebitda_last_5_years as json))).value AS revenue
    from public.ticker_revenue_data
    where stock_symbol = '{stock_symbol}'
    
    union all 
    
    SELECT (json_each(cast(ebitda_last_5_years as json))).key AS "Reporting Date", 
    (json_each(cast(ebitda_last_5_years as json))).value AS revenue
    from public.ticker_revenue_data_russell
    where stock_symbol = '{stock_symbol}'
    )
    
    select "Reporting Date", (replace(revenue::text, '"', '')::DECIMAL) as "Quarterly Revenue" from a 
    order by "Reporting Date" desc
    '''
    df_results = pd.read_sql(query_results, con=connect)
    # df_results['Quarterly Revenue'] = df_results['Quarterly Revenue'].apply(format_rounded_dollar)

    return df_results

