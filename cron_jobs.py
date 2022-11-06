import dataframes_from_queries
import schedule
import pandas as pd
from pandas_datareader import data
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
import time
from sqlalchemy import create_engine
import psycopg2
import passwords

url = passwords.rds_access

engine = create_engine(url)
connect = engine.connect()

today = date.today()
yesterdays_date = today - timedelta(days=1)
yesterdays_date = str(yesterdays_date)
year = int(yesterdays_date[0:4])
month = int(yesterdays_date[5:7])
day = int(yesterdays_date[8:10])

start_date = str(date(year, month, day))
end_date = str(date(year, month, day))

symbols_list = dataframes_from_queries.stock_dropdown()
# symbols_list = ['COIN', 'AAPL', 'AMC', 'GME', 'F', 'AAL', 'AMZN', 'GOOGL', 'GE', 'CRM', 'DDOG']

def append_to_postgres(df, table, append_or_replace):
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
            downloaded_data = data.DataReader(ticker, 'yahoo', f'{start_date}', f'{end_date}')
        except (ValueError, KeyError) as error:
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
    append_to_postgres(full_df, 'keyword_weekly_counts', 'replace')
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
    append_to_postgres(query_results_df, 'weekly_stock_openings', 'replace')
    print("Stock Window Functions Done")


# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(update_stock_data, 'cron', hour=7, minute=47)
#     scheduler.add_job(keyword_count_cron_job, 'cron', hour=7, minute=13)
#     scheduler.add_job(weekly_stock_opening_cron_job, 'cron', hour=7, minute=14)
#     scheduler.start()
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
# # day_of_week='tue-sat'
#
#     try:
#         # This is here to simulate application activity (which keeps the main thread alive).
#         while True:
#             time.sleep(2)
#     except (KeyboardInterrupt, SystemExit):
#         # Not strictly necessary if daemonic mode is enabled but should be done if possible
#         scheduler.shutdown()
