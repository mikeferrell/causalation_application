import dataframes_from_queries
import pandas as pd
from datetime import date, timedelta, datetime
from sqlalchemy import create_engine
import psycopg2
import passwords


url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

symbols_list = dataframes_from_queries.stock_dropdown()
 # symbols_list = ['COIN', 'AAPL']

#returns a string
def get_dates():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    year = int(yesterdays_date[0:4])
    month = int(yesterdays_date[5:7])
    day = int(yesterdays_date[8:10])

    yesterday = str(date(year, month, day))
    return yesterday

def get_datestoo():
    today = date.today()
    yesterday = today - timedelta(days=3)
    return yesterday


def append_to_postgres(df, table, append_or_replace):
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    find_open_queries = f'''
            SELECT pid FROM pg_locks l
            JOIN pg_class t ON l.relation = t.oid AND t.relkind = 'r'
            WHERE t.relname = '{table}'
            '''
    pid_list = pd.read_sql(find_open_queries, con=conn)
    pid_list = pid_list.values.tolist()
    for pids in pid_list:
        for pid in pids:
            kill_open_queries = f'''
                SELECT pg_terminate_backend({pid});
                '''
            kill_list = pd.read_sql(kill_open_queries, con=conn)
            print(kill_list)
    print("query killed to prep for upload")
    df = df
    try:
        df.to_sql(table, con=conn, if_exists=append_or_replace,
                  index=False)
        conn = psycopg2.connect(conn_string
                                )
        conn.autocommit = True
        cursor = conn.cursor()
        conn.close()
    except Exception as e:
        print('Error: ', e)
        conn.rollback()


#see if there's a more efficient way to ensure that for the correlation query, we only check timelines of between, idk
# 12 and 52 weeks. or less. No need to try every month. So do some filtering on the dates_dict within the end_dates
#portion of the for loop to reduce that. Right now, we're looking at generating 3.7MM rows
def top_correlation_scores():
    # grab the keywords we want to test
    keywords_dict = dataframes_from_queries.keyword_list
    end_dates_query = f'''
        select distinct(to_char(week_opening_date, 'YYYY-MM-DD')) as date_strings
        from public.weekly_stock_openings
        where week_opening_date is not null
        and week_opening_date >= '2022-08-01'
        and week_opening_date <= '{get_dates()}'
        order by  date_strings asc
        '''
    end_dates = pd.read_sql(end_dates_query, con=connect)
    end_dates = end_dates['date_strings'].tolist()
    # time delays to test
    time_delay_dict = ['1', '2', '4', '8', '12']
    filing_type = ['10-K', '10-Q']
    # grab the first date of each week within the time bound we're interested in. Right now, Aug 2021-Yesterday
    dates_dict = f'''
            with first_week_dates as (
            with temp_table as (
            select DATE_TRUNC('month',created_at) as created_at, close_price, stock_symbol
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
              end as weekly_closing_price
            FROM
              temp_table
              where stock_symbol = 'CRM')

            select to_char(weekly_closing_price, 'YYYY-MM-DD') as date_strings from first_week_dates
            where weekly_closing_price is not null
            and weekly_closing_price >= '2021-08-01'
            and weekly_closing_price <= '{get_dates()}'
        '''
    dates_dict = pd.read_sql(dates_dict, con=connect)
    dates_dict = dates_dict['date_strings'].tolist()

    list_of_all_correlations = []
    print("starting correlation for loop")
    for end_date in end_dates:
        for dates in dates_dict:
            for time_delays in time_delay_dict:
                for keywords in keywords_dict:
                    for filings in filing_type:
                        # Pulls the top 10 stock correlation scores with the applied filters
                        query_results = f'''
                            with top_correlations as (with rolling_average_calculation as (
                             with keyword_data as (select * from keyword_weekly_counts where keyword = '{keywords}'),
                            stock_weekly_opening as (select * from weekly_stock_openings)
    
                            select 
                            distinct week_opening_date
                            , week_close_price
                            , stock_symbol
                            , 1.00 * keyword_mentions / total_filings as keyword_percentage
                            from stock_weekly_opening 
                            join keyword_data 
                            on stock_weekly_opening.week_opening_date = keyword_data.filing_week + interval '{time_delays} week'
                            where week_opening_date >= '{dates}'
                            and week_opening_date <= '{get_dates()}'
                            and filing_type = '{filings}'
                            )
    
                            select week_opening_date, stock_symbol,
                            week_close_price,
                            'keyword Mentions' as keyword_mentions,
                            avg(keyword_percentage) over(order by stock_symbol, week_opening_date rows 12 preceding) as keyword_mentions_rolling_avg
                            from rolling_average_calculation
                            order by stock_symbol, week_opening_date
                            )
    
                            select stock_symbol, '{keywords} Mentions' as "Keyword",
                            '{dates}' as start_date,
                            '{end_date}' as end_date,
                            {time_delays} as time_delay,
                            '{filings}' as filing_type,
                            corr(week_close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
                            from top_correlations
                            where week_opening_date >= '{dates}'
                            and week_opening_date <= '{end_date}'
                            group by 1, 2
                            order by Correlation desc
                            limit 10
                            '''
                        df_results = pd.read_sql(query_results, con=connect)
                        df_results = df_results.round({'correlation': 4})
                        list_of_all_correlations.append(df_results)

    list_of_all_correlations = pd.concat(list_of_all_correlations, ignore_index=True)
    print("finished correlation for loop")
    df = pd.DataFrame(list_of_all_correlations)
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    df.to_sql('correlation_scores_for_backtest', con=conn, if_exists='replace',
              index=False)
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    conn.close()
    print("done with top correlations")