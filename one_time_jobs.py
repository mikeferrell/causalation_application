from ml_models import dataframes_from_queries
import pandas as pd
from datetime import date, timedelta, datetime
import time
from sqlalchemy import create_engine
from sec_edgar_downloader import Downloader
import psycopg2
import passwords
import edgar_jobs
import requests
import json
import yfinance as yf
import static.stock_list as stock_list

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
            dl.get(f"{filing_type}", f"{ticker}", after=start_date, before=f"{get_dates()}")
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

#remember to drop duplicates after running this. figure out if I can add a drop dupes line before uploading
#last ran on 10/7/23
def full_edgar_job_10ks():
    update_edgar_files('10-K', "2023-09-30")
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10k')
    time.sleep(5)
    edgar_jobs.delete_edgar_file_paths()
    print("done with edgar cron job")


#last ran on 9/30/23
def full_edgar_job_10qs():
    update_edgar_files('10-Q', "2023-09-30")
    time.sleep(10)
    edgar_jobs.analyze_edgar_files('10q')
    time.sleep(5)
    edgar_jobs.delete_edgar_file_paths()
    print("done with edgar cron job")

#
# full_edgar_job_10ks()
# time.sleep(60)
# full_edgar_job_10qs()


symbols_list = ['^SP500TR']
# symbols_list = stock_list.russell_finance_and_technology
# symbols_list = dataframes_from_queries.stock_dropdown()

def one_time_update_stock_data():
    symbols = []
    for ticker in symbols_list:
        try:
            downloaded_data = yf.download(ticker, start='2017-01-01', end='2020-12-31')
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

# one_time_update_stock_data()

def upload_csv_to_postgres():
    df = pd.read_csv('/Users/michaelferrell/PycharmProjects/causalation_dashboard/static/company_name.csv')
    append_to_postgres(df, 'stock_names', 'replace')

# upload_csv_to_postgres()

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


##______________##

##Alpha Vantage company data one time pulls

##______________##



def stock_earnings_data(start_symbol):
    symbols_list = stock_list.stock_list
    if start_symbol:
        start_index = symbols_list.index(start_symbol) + 1
        symbols_list = symbols_list[start_index:]

    df_for_pg_upload = pd.DataFrame(columns=['stock_symbol', 'peak_price_reported_eps', 'peak_price_eps_date',
                                             'most_recent_reported_eps', 'most_recent_eps_date'])
    api_limit = 499
    api_calls = 0

    # Create a list of dates associated with the max prices
    query_df = f'''
    select stock_symbol, date(created_at) as created_at, close_price 
    from ticker_data
    '''
    df_results = pd.read_sql(query_df, con=connect)
    max_price_date_df = df_results.loc[df_results.groupby('stock_symbol')['close_price'].idxmax()]
    max_price_date_df = max_price_date_df.drop(columns=['close_price'])

    for symbol in symbols_list:
        print(api_calls)
        if api_calls >= api_limit:
            # Handle the daily limit of API calls and end the loop
            print("API limit reached. Ending the loop.")
            break

        # Select date for the max price from above
        max_price_row = max_price_date_df.loc[max_price_date_df['stock_symbol'] == symbol]
        max_price_date = str(max_price_row.at[max_price_row.index[0], 'created_at'])

        # Pull earnings data
        try:
            earning_url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={passwords.alpha_vantage_api}'
            r = requests.get(earning_url)
            data = r.json()

            # Most recent earnings data
            most_recent_earnings_report = data["quarterlyEarnings"]
            most_recent_reported_eps = most_recent_earnings_report[0]["reportedEPS"]
            most_recent_eps_date = most_recent_earnings_report[0]["fiscalDateEnding"]

            # Earnings data at stock peak
            max_price_date = datetime.strptime(max_price_date, "%Y-%m-%d")
            filtered_earnings = [earnings for earnings in data["quarterlyEarnings"]
                                 if datetime.strptime(earnings["fiscalDateEnding"], "%Y-%m-%d") > max_price_date]
            sorted_earnings = sorted(filtered_earnings,
                                     key=lambda x: datetime.strptime(x["fiscalDateEnding"], "%Y-%m-%d"))

            if sorted_earnings:
                reported_eps = sorted_earnings[0]["reportedEPS"]
                peak_price_eps_date = sorted_earnings[0]["fiscalDateEnding"]
                peak_price_reported_eps = round(float(reported_eps), 2)
            else:
                pass

            # Build a df row with all the data to append to the full df for upload to postgres
            df_full = pd.DataFrame({
                'stock_symbol': [symbol],
                'peak_price_reported_eps': [peak_price_reported_eps],
                'peak_price_eps_date': [peak_price_eps_date],
                'most_recent_reported_eps': [most_recent_reported_eps],
                'most_recent_eps_date': [most_recent_eps_date]
            })
            df_for_pg_upload = df_for_pg_upload.append(df_full, ignore_index=True)

            api_calls += 1
            time.sleep(13)

        except Exception as e:
            print(f"Error occurred for symbol '{symbol}': {e}")
            continue

    append_to_postgres(df_for_pg_upload, 'eps_for_russell_3k', 'append')
    print(df_for_pg_upload)


#test first, then rerun to add everything from the russell3k over the next few days. once that's done, can do the other
#below jobs with only the technology companies
def pull_sector_data(start_symbol):
    symbols_list = [item for item in stock_list.russell3k if item not in stock_list.stock_list]
    symbols_list = ['^GSPC', 'SNOW']
    if start_symbol:
        start_index = symbols_list.index(start_symbol) + 1
        symbols_list = symbols_list[start_index:]

    df_for_pg_upload = pd.DataFrame(columns=['Symbol', 'Sector', 'PERatio', 'EVToEBITDA'])
    api_limit = 499
    api_calls = 0

    for symbol in symbols_list:
        print(api_calls)
        if api_calls >= api_limit:
            # Handle the daily limit of API calls and end the loop
            print("API limit reached. Ending the loop.")
            last_processed_symbol = symbol  # Store the value of the most recent symbol
            print(last_processed_symbol)
            break
        try:
            overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={passwords.alpha_vantage_api}'
            response = requests.get(overview_url)
            data = response.json()
            sector = data['Sector']
            pe_ratio = data['PERatio']
            ev_to_ebitda = data['EVToEBITDA']
            df_for_pg_upload = df_for_pg_upload.append({'stock_symbol': symbol, 'sector': sector, 'peratio': pe_ratio,
                                                        'evtoebitda': ev_to_ebitda},
                                                       ignore_index=True)

            api_calls += 1
            time.sleep(13)
        except Exception as e:
            print(f"Error occurred for symbol '{symbol}': {e}")
            continue
    append_to_postgres(df_for_pg_upload, 'ticker_sectors', 'append')
    print(df_for_pg_upload)


def income_statement_data(start_symbol):
    symbols_list = stock_list.russell_finance_and_technology
    symbols_list = ['^GSPC', 'SNOW']
    if start_symbol:
        start_index = symbols_list.index(start_symbol) + 1
        symbols_list = symbols_list[start_index:]

    df_for_pg_upload = pd.DataFrame(columns=['stock_symbol', 'peak_price_ebitda', 'peak_price_ebitda_date',
                                             'ebitda_last_5_years', 'most_recent_ebitda',
                                             'most_recent_ebitda_date'])
    api_limit = 499
    api_calls = 0

    # Create a list of dates associated with the max prices
    query_df = f'''
    select stock_symbol, date(created_at) as created_at, close_price 
    from ticker_data
    '''
    df_results = pd.read_sql(query_df, con=connect)
    max_price_date_df = df_results.loc[df_results.groupby('stock_symbol')['close_price'].idxmax()]
    max_price_date_df = max_price_date_df.drop(columns=['close_price'])

    for symbol in symbols_list:
        print(api_calls)
        if api_calls >= api_limit:
            # Handle the daily limit of API calls and end the loop
            print("API limit reached. Ending the loop.")
            break

        # Select date for the max price from above
        max_price_row = max_price_date_df.loc[max_price_date_df['stock_symbol'] == symbol]
        max_price_date = str(max_price_row.at[max_price_row.index[0], 'created_at'])

        # Pull earnings data
        try:
            icome_statement_url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={passwords.alpha_vantage_api}'
            r = requests.get(icome_statement_url)
            data = r.json()

            # Most recent revenue data
            most_recent_earnings_report = data["quarterlyReports"]
            most_recent_annual_revenue = most_recent_earnings_report[0]["ebitda"]
            most_recent_revenue_date = most_recent_earnings_report[0]["fiscalDateEnding"]

            # Earnings data at stock peak
            max_price_date = datetime.strptime(max_price_date, "%Y-%m-%d")
            filtered_earnings = [earnings for earnings in data["quarterlyReports"]
                                 if datetime.strptime(earnings["fiscalDateEnding"], "%Y-%m-%d") > max_price_date]
            if not filtered_earnings:
                filtered_earnings = [max(data["quarterlyReports"],
                                         key=lambda x: datetime.strptime(x["fiscalDateEnding"], "%Y-%m-%d"))]
            sorted_earnings = sorted(filtered_earnings,
                                     key=lambda x: datetime.strptime(x["fiscalDateEnding"], "%Y-%m-%d"))

            # Earnings over the last 5 years
            revenue_last_5_years = {}
            for report in most_recent_earnings_report[:20]:
                try:
                    fiscal_date_ending = report['fiscalDateEnding']
                    total_revenue = report['ebitda']
                    revenue_last_5_years[fiscal_date_ending] = total_revenue
                except Exception as e:
                    print("error:", e)
                    pass
            last_5_years_revenue_json = json.dumps(revenue_last_5_years)

            if sorted_earnings:
                peak_price_annual_revenue = sorted_earnings[0]["ebitda"]
                peak_price_revenue_date = sorted_earnings[0]["fiscalDateEnding"]
            else:
                pass


            # Build a df row with all the data to append to the full df for upload to postgres
            df_full = pd.DataFrame({
                'stock_symbol': [symbol],
                'peak_price_ebitda': [peak_price_annual_revenue],
                'peak_price_ebitda_date': [peak_price_revenue_date],
                'ebitda_last_5_years': [last_5_years_revenue_json],
                'most_recent_ebitda': [most_recent_annual_revenue],
                'most_recent_ebitda_date': [most_recent_revenue_date]
            })
            df_for_pg_upload = df_for_pg_upload.append(df_full, ignore_index=True)

            api_calls += 1
            time.sleep(13)

        except Exception as e:
            print(f"Error occurred for symbol '{symbol}': {e}")
            continue

    # append_to_postgres(df_for_pg_upload, 'ticker_revenue_data', 'append')
    print(df_for_pg_upload)


#can find shares outstanding point in time. need to fix everything below though
def balance_sheet_data(start_symbol):
    symbols_list = stock_list.russell_finance_and_technology
    symbols_list = ['^GSPC', 'SNOW']
    if start_symbol:
        start_index = symbols_list.index(start_symbol) + 1
        symbols_list = symbols_list[start_index:]

    df_for_pg_upload = pd.DataFrame()

    api_limit = 498
    api_calls = 0

    # Create a list of dates associated with the max prices
    query_df = f'''
    select stock_symbol, date(created_at) as created_at, close_price 
    from ticker_data
    '''
    df_results = pd.read_sql(query_df, con=connect)
    max_price_date_df = df_results.loc[df_results.groupby('stock_symbol')['close_price'].idxmax()]
    max_price_date_df = max_price_date_df.drop(columns=['close_price'])

    for symbol in symbols_list:
        print(api_calls)
        if api_calls >= api_limit:
            # Handle the daily limit of API calls and end the loop
            print("API limit reached. Ending the loop.")
            break

        # Select date for the max price from above
        max_price_row = max_price_date_df.loc[max_price_date_df['stock_symbol'] == symbol]
        max_price_date = str(max_price_row.at[max_price_row.index[0], 'created_at'])

        # Pull earnings data
        try:
            income_statement_url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={passwords.alpha_vantage_api}'
            r = requests.get(income_statement_url)
            data = r.json()

            # Most recent balance sheet data
            most_recent_earnings_report = data["quarterlyReports"]
            most_recent_shares_outstanding = most_recent_earnings_report[0]["commonStockSharesOutstanding"]
            most_recent_total_assets = most_recent_earnings_report[0]["totalAssets"]
            most_recent_total_cash_and_equivelants = most_recent_earnings_report[0]["cashAndCashEquivalentsAtCarryingValue"]
            most_recent_shares_date = most_recent_earnings_report[0]["fiscalDateEnding"]

            # data at stock peak
            max_price_date = datetime.strptime(max_price_date, "%Y-%m-%d")
            filtered_earnings = [earnings for earnings in data["quarterlyReports"]
                                 if datetime.strptime(earnings["fiscalDateEnding"], "%Y-%m-%d") > max_price_date]
            if not filtered_earnings:
                filtered_earnings = [max(data["quarterlyReports"],
                                         key=lambda x: datetime.strptime(x["fiscalDateEnding"], "%Y-%m-%d"))]
            sorted_earnings = sorted(filtered_earnings,
                                     key=lambda x: datetime.strptime(x["fiscalDateEnding"], "%Y-%m-%d"))
            # print('most recent', most_recent_earnings_report, 'filtered', filtered_earnings)

            if sorted_earnings:
                peak_price_shares_outstanding = sorted_earnings[0]["commonStockSharesOutstanding"]
                peak_price_total_assets = sorted_earnings[0]["totalAssets"]
                peak_price_total_cash_and_equivelants = sorted_earnings[0]["cashAndCashEquivalentsAtCarryingValue"]
                peak_price_revenue_date = sorted_earnings[0]["fiscalDateEnding"]
            else:
                pass


            # Build a df row with all the data to append to the full df for upload to postgres
            df_full = pd.DataFrame({
                'stock_symbol': [symbol],
                'peak_price_shares_outstanding': [peak_price_shares_outstanding],
                'peak_price_total_assets': [peak_price_total_assets],
                'peak_price_total_cash_and_equivelants': [peak_price_total_cash_and_equivelants],
                'peak_price_revenue_date': [peak_price_revenue_date],
                'most_recent_shares_outstanding': [most_recent_shares_outstanding],
                'most_recent_total_assets': [most_recent_total_assets],
                'most_recent_total_cash_and_equivelants': [most_recent_total_cash_and_equivelants],
                'most_recent_shares_date': [most_recent_shares_date]
            })
            df_for_pg_upload = df_for_pg_upload.append(df_full, ignore_index=True)

            api_calls += 1
            time.sleep(13)

        except Exception as e:
            print(f"Error occurred for symbol '{symbol}': {e}")
            continue

    append_to_postgres(df_for_pg_upload, 'ticker_balance_sheet_data', 'append')
    print(df_for_pg_upload)


#Need to run income statement data tomorrow
# pull_sector_data('^GSPC')
# income_statement_data('^GSPC')
# balance_sheet_data('^GSPC')



