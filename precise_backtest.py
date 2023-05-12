import dataframes_from_queries
from datetime import date, timedelta, datetime
from sqlalchemy import create_engine
import psycopg2
import passwords
import pandas as pd
from datetime import date, timedelta, datetime
from pandasql import sqldf
import numpy as np
from sklearn import datasets
import ml_models.forecast_top_stocks_model as forecast_top_stocks_model

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


def format_percent(value):
    return "{:.0%}".format(value)

def format_dollar(value):
    return "${:.2f}".format(value)


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

    today_minus_one_eighty = today - timedelta(days=180)
    return yesterday, today_minus_one_eighty

# def backtest_correlation_scores():
#see if there's a more efficient way to ensure that for the correlation query, we only check timelines of between, idk
# 12 and 52 weeks. or less. No need to try every month. So do some filtering on the dates_dict within the end_dates
#portion of the for loop to reduce that. Right now, we're looking at generating 3.7MM rows
#did this, double check the expected size output now and estimate time to run. this may work now, or may need more work

#
# def all_time_top_correlation_query_results():
#     end_dates_query = f'''
#     select distinct end_date from correlation_scores_for_backtest
#     order by end_date asc
#     '''
#     end_date_df = pd.read_sql(end_dates_query, con=connect)
#     end_date_list = end_date_df.values.tolist()
#
#     df_for_top_correlations = pd.DataFrame(columns=['stock_symbol', 'keyword', 'start_date', 'end_date', 'time_delay',
#                                                     'filing_type', 'correlation'])
#
#     for dates in end_date_list:
#         dates = dates[0]
#         top_correlation_query_results = f'''
#             with top_correlations as (
#             select stock_symbol
#             , split_part("Keyword", ' Mentions', 1) as keyword
#             , start_date
#             , end_date
#             , time_delay
#             , filing_type
#             , correlation
#             from public.correlation_scores_for_backtest
#             where correlation is not null
#               and date(start_date) <= current_date - interval '40 week'
#               and stock_symbol not in ('GEHC', 'CAH')
#               and correlation != 1
#               and "Keyword" != 'cryptocurrency Mentions'
#               and end_date = '{dates}'
#             order by correlation desc
#             limit 100
#             )
#
#             select distinct on (stock_symbol) *
#             from top_correlations
#             order by stock_symbol, correlation desc
#         '''
#         query_df = pd.read_sql(top_correlation_query_results, con=connect)
#         df_for_top_correlations = df_for_top_correlations.append(query_df, ignore_index=True)
#     return df_for_top_correlations


def build_backtest_prediction_table(model_type):
    df_for_calculating_backtest = pd.DataFrame(columns=['current_week', 'week_opening_date', 'keyword_mentions_rolling_avg',
                                             'current_close_price', 'next_week_close_price', 'predicted_price',
                                             'stock_symbol', 'keyword', 'start_date', 'monday_end_date',
                                             'friday_end_date', 'time_delay', 'filing_type'])

    #find each end date, then use that for the backtest process. exclude recent results where we might have incomplete data
    today = date.today()
    end_dates_query = f'''
    select distinct end_date from correlation_scores_for_backtest
    where date(end_date) <= date('{today}') - interval '14 day'
    order by end_date asc
    '''
    end_date_df = pd.read_sql(end_dates_query, con=connect)
    end_date_list = end_date_df.values.tolist()
    # print("end date list", end_date_list)
    #for each week in the table, find the top 10 correlation scores and return them
    for dates in end_date_list:
        dates = dates[0]
        # print("date for lopp", dates)
        top_correlation_query_results = f'''
            with top_correlations as (
            select stock_symbol
            , split_part("Keyword", ' Mentions', 1) as keyword
            , start_date
            , end_date
            , time_delay
            , filing_type
            , correlation
            from public.correlation_scores_for_backtest
            where correlation is not null
              and date(start_date) <= current_date - interval '40 week'
              and stock_symbol not in ('GEHC', 'CAH')
              and correlation != 1
              and "Keyword" != 'cryptocurrency Mentions'
              and end_date = '{dates}'
            order by correlation desc
            limit 250
            )

            select distinct on (stock_symbol) *
            from top_correlations
            order by stock_symbol, correlation desc
        '''
        query_df = pd.read_sql(top_correlation_query_results, con=connect)
        query_df = query_df.sort_values(by=['correlation'], ascending=False)
        query_df = query_df.head(10)
        # print("head sorted", query_df)

        test_results = []
        full_test_data = []
        stock_symbol_list = []
        keyword_list = []
        correlation_start_date_list = []
        friday_end_date_list = []
        monday_end_date_list = []
        interval_list = []
        filing_type_list = []

        row_range = range(0, 10)
        #for each of the top 10 correlation scores for each week, train the ML model then predict the following weekly
        # close (while hiding what that data is from the model)
        for rows in row_range:
            df_row = query_df.iloc[rows]
            stock_symbol = df_row['stock_symbol']
            keyword = df_row['keyword']
            correlation_start_date = df_row['start_date']
            monday_end_date = df_row['end_date']
            interval = df_row['time_delay']
            filing_type = df_row['filing_type']

            #adjusts start date and end dates to the real start & end dates as pulled from the DB
            #rounded_friday is the friday occuring before the last week of the data returned. Should it be the next Friday?
            #because we are returning data for the week of the monday_end_date. Fix this if we use friday_end_date for
            #anything important
            correlation_start_date = datetime.strptime(correlation_start_date, '%Y-%m-%d').date()
            correlation_start_date = correlation_start_date + timedelta((0 - correlation_start_date.weekday()) % 7)
            monday_end_date = datetime.strptime(monday_end_date, '%Y-%m-%d').date()
            rounded_friday = monday_end_date + timedelta(days=(4 - monday_end_date.weekday()))
            if rounded_friday == monday_end_date:
                rounded_friday = rounded_friday
            else:
                rounded_friday = rounded_friday - timedelta(days=7)
            friday_end_date = rounded_friday

            # print("row data", stock_symbol, keyword, correlation_start_date, monday_end_date, interval, filing_type)
            df_test_full, df_test, mae, model = forecast_top_stocks_model.train_narrow_ml_model(keyword, filing_type,
                                                                            stock_symbol, interval, monday_end_date,
                                                                            correlation_start_date, model_type)

            # print("df test full", df_test_full)
            full_test_data.append(df_test_full)
            try:
                prediction = model.predict(df_test)
                test_results.append(prediction)
                # print('Predicted stock price:', prediction)
            except (KeyError, ValueError) as error:
                print(error)
                continue

            # print("prediction", prediction)
            stock_symbol_list.append(stock_symbol)
            keyword_list.append(keyword)
            correlation_start_date_list.append(correlation_start_date)
            friday_end_date_list.append(friday_end_date)
            monday_end_date_list.append(monday_end_date)
            interval_list.append(interval)
            filing_type_list.append(filing_type)

        #build the table with all of the predictions
        # pd.set_option("display.max_columns", 20)
        print("start:", correlation_start_date_list, "end:", monday_end_date_list)
        print(stock_symbol_list)
        df_test = pd.DataFrame(test_results, columns=['predicted_price'])
        full_results_df = pd.concat(full_test_data, ignore_index=True)
        df_full = pd.DataFrame(full_results_df)
        df_full['predicted_price'] = df_test
        df_full['stock_symbol'] = stock_symbol_list
        df_full['keyword'] = keyword_list
        df_full['start_date'] = correlation_start_date_list
        df_full['friday_end_date'] = friday_end_date_list
        df_full['monday_end_date'] = monday_end_date_list
        df_full['time_delay'] = interval_list
        df_full['filing_type'] = filing_type_list
        df_full = df_full.drop_duplicates()
        # print("df full", df_full)
        df_for_calculating_backtest = df_for_calculating_backtest.append(df_full, ignore_index=True)
    return df_for_calculating_backtest

# model_type = 'random_forest'
# df_for_calculating_backtest = build_backtest_prediction_table(model_type)
# print(df_for_calculating_backtest)
# forecast_top_stocks_model.append_to_postgres(df_for_calculating_backtest, f'{model_type}_backtest_top_predictions_2', 'replace')

#model_type options are decision_tree, random_forest, and linear
def backtesting_buy_recommendation_list(model_type):
    buy_rec_query = f'''
        with stock_opening_dates as ( 
        with distinct_dates as (
        select distinct week_opening_date as week_opening_date
        from public.weekly_stock_openings 
        order by week_opening_date asc
        )
        select week_opening_date
        , LEAD(week_opening_date) OVER (ORDER BY week_opening_date) as next_week_opening_date
        from distinct_dates
        order by week_opening_date asc
        )
        
        select 
            next_week_opening_date as week_to_buy
          , {model_type}_backtest_top_predictions.stock_symbol
          , start_date, keyword, time_delay, filing_type
          , current_close_price
          , predicted_price
          , (predicted_price / {model_type}_backtest_top_predictions.current_close_price) - 1 as predicted_price_change_percentage
          , case 
            when current_close_price < predicted_price then 'buy recommended'
            else 'dont buy'
            end as predicted_price_movement
            , weekly_stock_openings.week_open_price as buy_open_price
          , weekly_stock_openings.week_close_price as buy_close_price
          from {model_type}_backtest_top_predictions
        JOIN stock_opening_dates on monday_end_date = stock_opening_dates.week_opening_date
        join public.weekly_stock_openings on stock_opening_dates.next_week_opening_date = weekly_stock_openings.week_opening_date
        and {model_type}_backtest_top_predictions.stock_symbol = weekly_stock_openings.stock_symbol
        order by monday_end_date
    '''
    buy_rec_df = pd.read_sql(buy_rec_query, con=connect)

    date_query = '''
    select distinct week_to_buy as buy_week from buy_rec_df
    '''
    df_for_buys = sqldf(date_query)
    # print("weeks", df_for_buys)

    cash_in_hand = 1000

    performance_at_each_week = []
    # Iterate through each unique buy_week date and calculate returns
    for index, row in df_for_buys.iterrows():
        buy_week = row['buy_week']
        #dataframe of which stocks to buy, and the weight for how many shares to buy
        query_for_buys = f'''
        with stock_selections as (
          SELECT
              stock_symbol,
              week_to_buy as buy_week,
              buy_open_price as buy_price,
              buy_close_price as cashout_price,
              predicted_price_change_percentage
          FROM
              buy_rec_df
            WHERE predicted_price_movement = 'buy recommended'
            and week_to_buy = '{buy_week}'
        ),

        total_estimation as (
          select buy_week
          , sum(predicted_price_change_percentage) total_prediction_changes
          from stock_selections
          group by buy_week
        )

        select 
          stock_symbol, 
          stock_selections.buy_week, 
          buy_price, 
          cashout_price,
          {cash_in_hand} * predicted_price_change_percentage / total_prediction_changes / buy_price as number_of_shares_to_buy
        from 
          stock_selections 
          join total_estimation on stock_selections.buy_week = total_estimation.buy_week
        where predicted_price_change_percentage != 0
        order by 
          stock_selections.buy_week asc
            '''
        df_for_calculating_returns = sqldf(query_for_buys)
        # print(df_for_calculating_returns)

        returns_for_date = ((df_for_calculating_returns['cashout_price'] * df_for_calculating_returns['number_of_shares_to_buy'])
                                             - (df_for_calculating_returns['buy_price'] * df_for_calculating_returns['number_of_shares_to_buy'])).sum()
        # print("returns", returns_for_date)

        # print("cash in hand before:", cash_in_hand)
        cash_in_hand = cash_in_hand + returns_for_date
        # print("cash in hand after:", cash_in_hand)
        end_of_week_performance = (buy_week, cash_in_hand)
        performance_at_each_week.append(end_of_week_performance)
    performance_at_each_week_df = pd.DataFrame(performance_at_each_week,
                                               columns=['week_of_purchases', 'portfolio_value'])

    #df to be displayed on the website
    buy_rec_df['predicted_price_change_percentage'] = buy_rec_df['predicted_price_change_percentage'].apply(format_percent)
    buy_rec_df['current_close_price'] = buy_rec_df['current_close_price'].apply(format_dollar)
    buy_rec_df['predicted_price'] = buy_rec_df['predicted_price'].apply(format_dollar)
    buy_rec_df['buy_open_price'] = buy_rec_df['buy_open_price'].apply(format_dollar)
    buy_rec_df['buy_close_price'] = buy_rec_df['buy_close_price'].apply(format_dollar)
    buy_rec_df['week_to_buy'] = pd.to_datetime(buy_rec_df['week_to_buy']).apply(lambda x: x.date())
    buy_rec_df.rename(columns={'predicted_price_change_percentage': 'Predicted Change',
                               'current_close_price': 'Close Price',
                               'predicted_price': 'Predicted Price',
                               'buy_open_price':'Purchase Price',
                               'buy_close_price':'Sale Price',
                               'predicted_price_movement':'Recommendation',
                               'week_to_buy':"Purchase Week"
                               }, inplace=True)
    buy_rec_df = buy_rec_df.drop(columns=['start_date', 'time_delay', 'filing_type'])

    return cash_in_hand, performance_at_each_week_df, buy_rec_df

# cash_in_hand, performance_at_each_week_df = backtesting_buy_recommendation_list('decision_tree')
# print(performance_at_each_week_df)


def comparing_returns_vs_sandp(model_type):
    returns_df = backtesting_buy_recommendation_list(model_type)[1]
    first_date = returns_df['week_of_purchases'].min()
    last_date = returns_df['week_of_purchases'].max()
    # print("full df", returns_df)

    sandp_query = f'''
    select created_at as week_of_purchases, close_price as s_and_p_price from ticker_data
    where stock_symbol = '^GSPC'
    and created_at >= '{first_date}'
    and created_at <= '{last_date}'
    order by created_at asc
    '''
    df_for_join = pd.read_sql(sandp_query, con=connect)
    df_for_join['week_of_purchases'] = pd.to_datetime(df_for_join['week_of_purchases'])
    returns_df['week_of_purchases'] = pd.to_datetime(returns_df['week_of_purchases'])
    df_for_chart = pd.merge(df_for_join, returns_df, how='inner', on='week_of_purchases')

    #calculate S&P ROI
    starting_price_sp = df_for_join['s_and_p_price'].values[:1]
    ending_price_sp = df_for_join['s_and_p_price'].values[-1:]
    starting_price_sp = starting_price_sp[0]
    ending_price_sp = ending_price_sp[0]
    s_and_p_returns = (ending_price_sp - starting_price_sp) / starting_price_sp
    s_and_p_number = s_and_p_returns
    s_and_p_returns = "{:.1%}".format(s_and_p_returns)

    # calculate Backtest ROI
    starting_price_backtest = returns_df['portfolio_value'].values[:1]
    ending_price_backtest = returns_df['portfolio_value'].values[-1:]
    starting_price_backtest = starting_price_backtest[0]
    ending_price_backtest = ending_price_backtest[0]
    backtest_returns = (ending_price_backtest - starting_price_backtest) / starting_price_backtest
    backtest_number = backtest_returns
    backtest_returns = "{:.1%}".format(backtest_returns)

    #calculate Sharpe Ratio. This first way is from the book, the second one looks cleaner
    # weekly_returns = np.log(1 + returns_df.loc[:, 'portfolio_value'].pct_change())
    # excess_returns = (weekly_returns-risk_free_rate)/52
    # sharpe_ratio = np.sqrt(52)*np.mean(excess_returns)/np.std(excess_returns)
    risk_free_rate = 0.04
    returns = np.log(returns_df['portfolio_value'] / returns_df['portfolio_value'].shift(1))
    volatility = returns.std() * np.sqrt(52)
    sharpe_ratio = ((returns.mean() * 52) - risk_free_rate) / volatility
    sharpe_ratio = round(sharpe_ratio, 3)
    return df_for_chart, s_and_p_returns, backtest_returns, sharpe_ratio, returns_df


# df_for_chart, s_and_p_returns, backtest_returns, sharpe_ratio, returns_df = comparing_returns_vs_sandp('random_forest')
# print(sharpe_ratio)
