import dataframes_from_queries
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta
import time
from sqlalchemy import create_engine
import psycopg2
import passwords
import edgar_jobs

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

today = date.today()
yesterdays_date = today - timedelta(days=1)
yesterdays_date = str(yesterdays_date)
year = int(yesterdays_date[0:4])
month = int(yesterdays_date[5:7])
day = int(yesterdays_date[8:10])

yesterday = str(date(year, month, day))
end_date = str(date(year, month, day))

symbols_list = dataframes_from_queries.stock_dropdown()
# symbols_list = ['COIN', 'AAPL', 'AMC', 'GME', 'F', 'AAL', 'AMZN', 'GOOGL', 'GE', 'CRM', 'DDOG']

def append_to_postgres(df, table, append_or_replace):
    df = df
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    df.to_sql(table, con=conn, if_exists=append_or_replace,
              index=False)
    conn = psycopg2.connect(conn_string
                            )
    conn.autocommit = True
    cursor = conn.cursor()
    conn.close()


def update_stock_data():
    symbols = []
    for ticker in symbols_list:
        try:
            downloaded_data = data.DataReader(ticker, 'yahoo', f'{yesterday}', f'{yesterday}')
        except (ValueError, KeyError, Exception) as error:
            print(f"{error} for {ticker}")
            continue
        downloaded_data['Symbol'] = ticker
        symbols.append(downloaded_data)
    df = pd.concat(symbols)
    df = df.reset_index()
    df = df[['Date', 'Close', 'Symbol']]
    df.columns = ['created_at', 'close_price', 'stock_symbol']
    df.head()
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
            where risk_factors != ''
            and risk_disclosures != ''
            order by inflation_count desc)

            select sum(inflation_count) as keyword_mentions,
            '{keywords}' as "keyword",
            count(filing_url) as total_filings,
            filing_type,
            DATE_TRUNC('week',filing_date) as filing_week
            from count_inflation_mentions
            group by filing_week, filing_type
            order by filing_week asc
            '''
        query_results_df = pd.read_sql(query_results, con=connect)
        full_df = full_df.append(query_results_df, ignore_index=True)
    append_to_postgres(full_df, 'keyword_weekly_counts_new', 'replace')
    print("Keywords Done")

def weekly_stock_opening_cron_job():
    query_results = f'''
        with temp_table as (
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
          temp_table
        '''
    query_results_df = pd.read_sql(query_results, con=connect)
    append_to_postgres(query_results_df, 'weekly_stock_openings_new', 'replace')
    print("Stock Window Functions Done")

# def listener(event):
#     print("starting listener", datetime.now())
#     if not event.exception:
#         job = scheduler.get_job(event.job_id)
#         if job.name == 'download_10ks':
#             scheduler.add_job(lambda: edgar_jobs.analyze_edgar_files_10k())
#             print("finished edgar jobs")
#     print("done with listener", datetime.now())

def full_edgar_job_10ks():
    edgar_jobs.update_edgar_10ks()
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10k')

def full_edgar_job_10qs():
    edgar_jobs.update_edgar_10qs()
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10q')


# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     # scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#     # scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#     # scheduler.add_job(full_edgar_job_10ks('cron', hour=10, minute=45, name='full_edgar_10ks')
#     # scheduler.add_job(full_edgar_job_10qs('cron', hour=10, minute=45, name='full_edgar_10qs')
#     # scheduler.add_job(update_stock_data, 'cron', hour=7, minute=47)
#     scheduler.add_job(keyword_count_cron_job, 'cron', hour=11, minute=15)
# #     scheduler.add_job(weekly_stock_opening_cron_job, 'cron', hour=11, minute=2)
#     scheduler.start()
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
# # # day_of_week='tue-sat'
#
#     try:
#         # This is here to simulate application activity (which keeps the main thread alive).
#         while True:
#             time.sleep(2)
#     except (KeyboardInterrupt, SystemExit):
#         # Not strictly necessary if daemonic mode is enabled but should be done if possible
#         scheduler.shutdown()
#

