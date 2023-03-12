import pandas as pd
from sqlalchemy import create_engine
import psycopg2

url = rds_access
engine = create_engine(url)
connect = engine.connect()


def append_to_postgres(df, table, append_or_replace):
    conn_string = rds_access
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
    print("query killed")
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


def weekly_stock_opening_cron_job():
    print("starting query")
    query_results = f'''
              with temp_table as (
              select DATE_TRUNC('week',created_at) as created_at, close_price, stock_symbol, created_at as actual_date
              from public.ticker_data
              order by stock_symbol, date(created_at)  asc
              )

            SELECT
                actual_date,
                created_at,
                close_price,
                stock_symbol,
                LAG(created_at,1) OVER (
                    ORDER BY stock_symbol, actual_date desc
                ) as next_date,
                    case when LAG(created_at) OVER (
                    ORDER BY stock_symbol, actual_date desc
                ) = created_at then null else created_at
                end as weekly_closing_price
            FROM
                temp_table
            '''
    query_results_df = pd.read_sql(query_results, con=connect)
    print("query done")
    append_to_postgres(query_results_df, 'weekly_stock_openings', 'replace')
    print("Stock Window Functions Done")

weekly_stock_opening_cron_job()