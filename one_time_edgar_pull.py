import dataframes_from_queries
import pandas as pd
from pandas_datareader import data
from datetime import date, timedelta, datetime
import time
from sqlalchemy import create_engine
from sec_edgar_downloader import Downloader
import psycopg2
import passwords
import edgar_jobs
from older_versions import top_correlations

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

symbols_list = dataframes_from_queries.stock_dropdown()


# symbols_list = ['COIN', 'AAPL']

def get_dates():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    year = int(yesterdays_date[0:4])
    month = int(yesterdays_date[5:7])
    day = int(yesterdays_date[8:10])

    yesterday = str(date(year, month, day))
    return yesterday


def update_edgar_files(filing_type, start_date):
    print("starting updates", datetime.now())
    for ticker in symbols_list:
        dl = Downloader()
        try:
            dl.get(f"{filing_type}", ticker, after=start_date, before=f"{get_dates()}")
        except Exception as error:
            print(error)
            continue
    print("ending updates", datetime.now())


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
            downloaded_data = data.DataReader(ticker, 'yahoo', '2017-01-01', '2022-12-04')
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




def full_edgar_job_10ks():
    update_edgar_files('10-K', "2022-08-18")
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10k')
    time.sleep(5)
    edgar_jobs.delete_edgar_file_paths()
    print("done with edgar cron job")


def full_edgar_job_10qs():
    update_edgar_files('10-Q', "2021-01-01")
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10q')
    time.sleep(5)
    edgar_jobs.delete_edgar_file_paths()
    print("done with edgar cron job")


def top_correlation_score_cron():
    top_correlations.top_correlation_scores()
    print("done with top correlation scores")

# def listener(event):
#     print("starting listener", datetime.now())
#     if not event.exception:
#         job = scheduler.get_job(event.job_id)
#         if job.name == 'download_10ks':
#             scheduler.add_job(lambda: edgar_jobs.analyze_edgar_files_10k())
#             print("finished edgar jobs")
#     print("done with listener", datetime.now())

# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     # scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#     # scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#     # scheduler.add_job(full_edgar_job_10ks, 'cron', hour=10, minute=45, name='full_edgar_10ks')
#     # scheduler.add_job(full_edgar_job_10qs, 'cron', hour=10, minute=45, name='full_edgar_10qs')
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