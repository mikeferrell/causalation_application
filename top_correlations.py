# import pandas as pd
# import passwords
# from sqlalchemy import create_engine
# import psycopg2
# import dataframes_from_queries
#
# url = passwords.rds_access
#
# engine = create_engine(url)
# connect = engine.connect()
#
# def top_correlation_scores():
#     # grab the keywords we want to test
#     keywords_dict = dataframes_from_queries.keyword_list
#     # time delays to test
#     time_delay_dict = ['4', '8', '12']
#     # grab the first date of each week within the time bound we're interested in
#     dates_dict = f'''
#             with first_week_dates as (
#             with temp_table as (
#             select DATE_TRUNC('month',created_at) as created_at, close_price, stock_symbol
#             from public.ticker_data
#             order by stock_symbol, date(created_at)  asc
#             )
#
#             SELECT
#               created_at,
#               close_price,
#               stock_symbol,
#               LAG(created_at,1) OVER (
#                   ORDER BY stock_symbol, created_at
#               ) as next_date,
#                   case when LAG(created_at) OVER (
#                   ORDER BY stock_symbol, created_at
#               ) = created_at then null else created_at
#               end as weekly_closing_price
#             FROM
#               temp_table
#               where stock_symbol = 'CRM')
#
#             select to_char(weekly_closing_price, 'YYYY-MM-DD') as date_strings from first_week_dates
#             where weekly_closing_price is not null
#             and weekly_closing_price >= '2018-01-01'
#             and weekly_closing_price <= '2022-01-01'
#         '''
#     dates_dict = pd.read_sql(dates_dict, con=connect)
#     dates_dict = dates_dict['date_strings'].tolist()
#
#     list_of_all_correlations = []
#     print("starting correlation for loop")
#
#     for dates in dates_dict:
#         for time_delays in time_delay_dict:
#             for keywords in keywords_dict:
#                     query_results = f'''
#                     with top_correlations as (with rolling_average_calculation as (
#                      with keyword_data as (select * from keyword_weekly_counts where keyword = '{keywords}'),
#                     stock_weekly_opening as (select * from weekly_stock_openings)
#
#                     select weekly_closing_price as stock_date, close_price, stock_symbol, 1.00 * keyword_mentions / total_filings as keyword_percentage
#                     from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week + interval '{time_delays} week'
#                     where weekly_closing_price >= '{dates}'
#                     and weekly_closing_price <= '2022-12-29'
#                     )
#
#                     select stock_date, stock_symbol,
#                     close_price,
#                     'keyword Mentions' as keyword_mentions,
#                     avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
#                     from rolling_average_calculation
#                     order by stock_symbol, stock_date
#                     )
#
#                     select stock_symbol as "Stock Symbol", '{keywords} Mentions' as "Keyword",
#                     '{dates}' as "Start Date",
#                     '2022-08-29' as "End Date",
#                     {time_delays} as time_delay,
#                     corr(close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
#                     from top_correlations
#                     where stock_date >= '{dates}'
#                     and stock_date <= '2022-08-29'
#                     group by 1, 2
#                     order by Correlation desc
#                     limit 10
#                         '''
#                     df_results = pd.read_sql(query_results, con=connect)
#                     df_results = df_results.round({'correlation': 4})
#                     list_of_all_correlations.append(df_results)
#
#     list_of_all_correlations = pd.concat(list_of_all_correlations, ignore_index=True)
#     print("finished correlation for loop")
#     df = pd.DataFrame(list_of_all_correlations)
#     conn_string = passwords.rds_access
#     db = create_engine(conn_string)
#     conn = db.connect()
#     df.to_sql('all_correlation_scores', con=conn, if_exists='replace',
#               index=False)
#     conn = psycopg2.connect(conn_string)
#     conn.autocommit = True
#     cursor = conn.cursor()
#     conn.close()
#     print('done')
#
# # for time_delays in time_delay_dict:
# #     query_results = f'''
# #             with top_correlations as (with rolling_average_calculation as (
# #                  with keyword_data as (select * from keyword_weekly_counts where keyword = 'cloud'),
# #                 stock_weekly_opening as (select * from weekly_stock_openings)
# #
# #                 select weekly_closing_price as stock_date, close_price, stock_symbol, 1.00 * keyword_mentions / total_filings as keyword_percentage
# #                 from stock_weekly_opening join keyword_data on stock_weekly_opening.weekly_closing_price = keyword_data.filing_week + interval '{time_delays} week'
# #                 where weekly_closing_price >= '2022-01-01'
# #                 and weekly_closing_price <= '2022-08-29'
# #                 )
# #
# #                 select stock_date, stock_symbol,
# #                 close_price,
# #                 'keyword Mentions' as keyword_mentions,
# #                 avg(keyword_percentage) over(order by stock_symbol, stock_date rows 12 preceding) as keyword_mentions_rolling_avg
# #                 from rolling_average_calculation
# #                 order by stock_symbol, stock_date
# #                 )
# #
# #             select stock_symbol as "Stock Symbol", 'cloud Mentions' as "Keyword Mentions",
# #              corr(close_price, keyword_mentions_rolling_avg) * 1.000 as Correlation
# #             from top_correlations
# #             where stock_date >= '2022-01-01'
# #             and stock_date <= '2022-08-29'
# #             and stock_symbol = 'ETSY'
# #             group by 1, 2
# #         '''
# #     df_results = pd.read_sql(query_results, con=connect)
# #     df_results = df_results.round({'correlation': 4})
# #     df_results = df_results.to_dict()
# #     list_of_all_correlations.append(df_results)
#
#
