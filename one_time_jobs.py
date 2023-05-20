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
import yfinance as yf
import top_correlations

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

symbols_list = dataframes_from_queries.stock_dropdown()


def get_dates():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    year = int(yesterdays_date[0:4])
    month = int(yesterdays_date[5:7])
    day = int(yesterdays_date[8:10])

    yesterday = str(date(year, month, day))
    return yesterday


def get_dates_multiple():
    today = date.today()
    yesterdays_date = today - timedelta(days=1)
    yesterdays_date = str(yesterdays_date)
    year = int(yesterdays_date[0:4])
    month = int(yesterdays_date[5:7])
    day = int(yesterdays_date[8:10])
    yesterday = str(date(year, month, day))

    today_minus_one_eighty = today - timedelta(days=180)
    return yesterday, today_minus_one_eighty


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


def full_edgar_job_10ks():
    update_edgar_files('10-K', "2023-02-24")
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10k')
    time.sleep(5)
    edgar_jobs.delete_edgar_file_paths()
    print("done with edgar cron job")


def full_edgar_job_10qs():
    update_edgar_files('10-Q', "2023-02-24")
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10q')
    time.sleep(5)
    edgar_jobs.delete_edgar_file_paths()
    print("done with edgar cron job")

# full_edgar_job_10ks()
# full_edgar_job_10qs()

# symbols_list = []

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
    append_to_postgres(df, 'ticker_data', 'append')
    print("stocks done")


def one_time_backfill_correlation_scores(asc_or_desc):
    yesterday, today_minus_one_eighty = get_dates_multiple()
    # grab the keywords we want to test
    keywords_dict = dataframes_from_queries.keyword_list
    # list of each week that will be used as the week for backtest
    end_dates_query = f'''
        select distinct(to_char(week_opening_date, 'YYYY-MM-DD')) as date_strings
        from public.weekly_stock_openings
        where week_opening_date is not null
        and week_opening_date >= '2022-09-26'
        and week_opening_date <= '{yesterday}'
        order by  date_strings asc
        '''
    #         and week_opening_date >= '{today_minus_one_eighty}'
    end_dates = pd.read_sql(end_dates_query, con=connect)
    end_dates = end_dates['date_strings'].tolist()
    # print(end_dates)
    # time delays to test
    time_delay_dict = ['1', '2', '4', '8']
    filing_type = ['10-K']
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
            and weekly_closing_price <= '{yesterday}'
        '''
    dates_dict = pd.read_sql(dates_dict, con=connect)
    dates_dict = dates_dict['date_strings'].tolist()

    list_of_all_correlations = []
    print("starting correlation for loop")
    for end_date in end_dates:
        for start_date in dates_dict:
            #only look at times where the start date is 6 months to 1 yr before the end date
            if (datetime.strptime(start_date, '%Y-%m-%d').date() >= (datetime.strptime(end_date, '%Y-%m-%d').date() -
                                                                     timedelta(days=365))) and (
                    datetime.strptime(start_date, '%Y-%m-%d').date()
                    <= (datetime.strptime(end_date, '%Y-%m-%d').date() - timedelta(days=180))):
                print("working", start_date, end_date)
                for time_delays in time_delay_dict:
                    for keywords in keywords_dict:
                        for filings in filing_type:
                            # Pulls the top 10 stock correlation scores with the applied filters
                            #end date is the Monday of the most recent week of stock data. So we have data for the
                            #end date week included in the results
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
                                where week_opening_date >= '{start_date}'
                                and week_opening_date <= '{yesterday}'
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
                                '{start_date}' as start_date,
                                '{end_date}' as end_date,
                                {time_delays} as time_delay,
                                '{filings}' as filing_type,
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
                            list_of_all_correlations.append(df_results)
    list_of_all_correlations = pd.concat(list_of_all_correlations, ignore_index=True)
    print("finished correlation for loop")
    if asc_or_desc == 'asc':
        append_to_postgres(list_of_all_correlations, 'inverse_correlation_scores_for_backtest', 'replace')
    if asc_or_desc == 'desc':
        append_to_postgres(list_of_all_correlations, 'correlation_scores_for_backtest', 'replace')
    else:
        pass
    print("done with top correlations")


def backfill_score_wrapper_asc():
    one_time_backfill_correlation_scores('asc')


def backfill_score_wrapper_desc():
    one_time_backfill_correlation_scores('desc')

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