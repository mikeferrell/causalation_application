import dataframes_from_queries
import os
import pandas as pd
import yfinance as yf
from datetime import date, timedelta, datetime
import time
from sqlalchemy import create_engine
from sec_edgar_downloader import Downloader
import psycopg2
import passwords
import edgar_jobs
import ml_models.forecast_top_stocks_model as forecast_top_stocks_model

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


def update_edgar_files(filing_type):
    print("starting updates", datetime.now())
    for ticker in symbols_list:
        dl = Downloader()
        try:
            dl.get(f"{filing_type}", ticker, after=f"{get_dates()}", before=f"{get_dates()}")
        except Exception as error:
            print(error)
            continue
    print("ending updates", datetime.now())


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


def update_stock_data():
    symbols = []
    for ticker in symbols_list:
        try:
            # downloaded_data = yf.download(ticker, start='2017-01-01', end=date.today())
            downloaded_data = yf.download(ticker, start=f'{get_dates()}', end=date.today())
        except (ValueError, KeyError, Exception) as error:
            print(f"{error} for {ticker}")
            continue
        downloaded_data['Symbol'] = ticker
        symbols.append(downloaded_data)
    df = pd.concat(symbols)
    df = df.reset_index()
    df = df[['Date', 'Close', 'Symbol']]
    df.columns = ['created_at', 'close_price', 'stock_symbol']
    df = df.drop_duplicates()
    append_to_postgres(df, 'ticker_data', 'append')
    print("Stock Done")


def keyword_count_cron_job():
    keyword_list = dataframes_from_queries.keyword_list
    full_df = pd.DataFrame(columns=['keyword_mentions', 'keyword', 'total_filings', 'filing_type', 'filing_week'])
    for keywords in keyword_list:
        query_results = f'''
          with count_inflation_mentions as (
          select date(filing_date) as filing_date,
          filing_url,
          filing_type,
          case when risk_factors ilike '%%{keywords}%%' then 1
          when risk_disclosures ilike '%%{keywords}%%' then 1
          else 0
          end as inflation_count
          from public.edgar_data
          order by filing_date desc)
        
          select sum(inflation_count) as keyword_mentions,
          '{keywords}' as "keyword",
          count(filing_url) as total_filings,
          filing_type,
          DATE_TRUNC('week',filing_date) as filing_week
          from count_inflation_mentions
          group by filing_week, filing_type
          order by filing_week desc
            '''
        query_results_df = pd.read_sql(query_results, con=connect)
        full_df = full_df.append(query_results_df, ignore_index=True)
    print("df_ready_to_write")
    append_to_postgres(full_df, 'keyword_weekly_counts', 'replace')
    print("Keywords Done")


def weekly_stock_opening_cron_job():
    print("starting weekly stock price query")
    query_results = f'''
          with table_for_join as (
          with temp_table as (
          select DATE_TRUNC('week',created_at) as week_of_prices, close_price, open_price, 
          stock_symbol, created_at as date_of_prices
          from public.ticker_data
          order by stock_symbol, date(created_at)  asc
          )
        
        SELECT
            date_of_prices,
            week_of_prices,
            close_price,
            open_price,
            stock_symbol,
            LAG(week_of_prices,1) OVER (
                ORDER BY stock_symbol, date_of_prices desc
            ) as next_date
                , case when LAG(week_of_prices) OVER (
                ORDER BY stock_symbol, date_of_prices desc
            ) = week_of_prices then null else week_of_prices
            end as weekly_closing_date
                , case when LAG(week_of_prices) OVER (
                ORDER BY stock_symbol, date_of_prices asc
            ) = week_of_prices then null else week_of_prices
            end as weekly_opening_date
        FROM
            temp_table
        Order by stock_symbol, date_of_prices asc
            )
            
        select a.stock_symbol
        , a.week_of_prices as week_opening_date
        , a.open_price as week_open_price
        , b.close_price as week_close_price
        from table_for_join as a 
        join table_for_join as b 
        on a.weekly_opening_date = b.weekly_closing_date
        and a.stock_symbol = b.stock_symbol
        where a.weekly_opening_date is not NULL 
        and b.weekly_closing_date is not null
        order by stock_symbol, week_opening_date asc
            '''
    query_results_df = pd.read_sql(query_results, con=connect)
    print("weekly stock price query done")
    append_to_postgres(query_results_df, 'weekly_stock_openings', 'replace')
    print("Weekly Stock Window Functions Done")


# For each critieria in the lists, pull the stocks with the top 10 correlation scores. Loop through all the different
# options
def top_correlation_scores():
    # grab the keywords we want to test
    keywords_dict = dataframes_from_queries.keyword_list
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
                        '{get_dates()}' as end_date,
                        {time_delays} as time_delay,
                        '{filings}' as filing_type,
                        corr(week_close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
                        from top_correlations
                        where week_opening_date >= '{dates}'
                        and week_opening_date <= '{get_dates()}'
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
    df.to_sql('all_correlation_scores', con=conn, if_exists='replace',
              index=False)
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    conn.close()
    print("done with top correlations")


def full_edgar_job_10ks():
    update_edgar_files('10-K')
    time.sleep(10)
    count = 0
    for root_dir, cur_dir, files in os.walk(r'sec-edgar-filings/'):
        count += len(files)
    if count > 1:
        edgar_jobs.analyze_edgar_files('10k')
        time.sleep(5)
        edgar_jobs.delete_edgar_file_paths()
    else:
        print("no files to analyze")
    print("done with 10k cron job")

def full_edgar_job_10qs():
    update_edgar_files('10-Q')
    time.sleep(10)
    count = 0
    for root_dir, cur_dir, files in os.walk(r'sec-edgar-filings/'):
        count += len(files)
    if count > 1:
        edgar_jobs.analyze_edgar_files('10q')
        time.sleep(5)
        edgar_jobs.delete_edgar_file_paths()
    else:
        print("no files to analyze")
    print("done with 10q cron job")

def ml_calculate_top_ten_forecasts():
    full_df_for_upload = forecast_top_stocks_model.calculate_top_ten_forecasts('backtest')
    append_to_postgres(full_df_for_upload, 'top_five_prediction_results', 'replace')


def one_time_update_stock_data():
    symbols = []
    for ticker in symbols_list:
        try:
            downloaded_data = yf.download(ticker, start='2017-01-01', end=date.today())
        except (ValueError, KeyError, Exception) as error:
            print(f"{error} for {ticker}")
            continue
        downloaded_data['Symbol'] = ticker
        symbols.append(downloaded_data)
    df = pd.concat(symbols)
    print(df)
    df = df.reset_index()
    df = df[['Date', 'Open', 'Close', 'Symbol']]
    df.columns = ['created_at', 'open_price', 'close_price', 'stock_symbol']
    df = df.drop_duplicates()
    append_to_postgres(df, 'ticker_data', 'replace')
    print("stocks done")
