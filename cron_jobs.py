import pandas as pd
import passwords
from sqlalchemy import create_engine
import psycopg2

url = passwords.rds_access

engine = create_engine(url)
connect = engine.connect()

# running once
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

df = weekly_stock_opening_cron_job()
df.head()
conn_string = passwords.rds_access
db = create_engine(conn_string)
conn = db.connect()
df.to_sql('weekly_stock_openings', con=conn, if_exists='replace',
          index=False)
conn = psycopg2.connect(conn_string)
conn.autocommit = True
cursor = conn.cursor()
conn.close()
print('done')

