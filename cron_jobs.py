import pandas as pd
import passwords
from sqlalchemy import create_engine
import psycopg2
import dataframes_from_queries
import schedule
import time

url = passwords.rds_access

engine = create_engine(url)
connect = engine.connect()

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
    return full_df

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
    return query_results_df

def update_daily_cron_job(which_task, which_table):
    df = which_task
    df.head()
    conn_string = passwords.rds_access
    db = create_engine(conn_string)
    conn = db.connect()
    df.to_sql(which_table, con=conn, if_exists='replace',
              index=False)
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    conn.close()
    print('done')

# keyword_schedule = schedule.every(1).day.at("05:30").do(
#     update_daily_cron_job(keyword_count_cron_job(), 'keyword_weekly_counts'))
# stock_schedule = schedule.every(1).day.at("06:00").do(
#     update_daily_cron_job(weekly_stock_opening_cron_job(), 'weekly_stock_openings'))