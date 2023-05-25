import pandas as pd
import passwords
from sqlalchemy import create_engine
from static.stock_list import stock_list
import ml_models.forecast_top_stocks_model_v2 as forecast_top_stocks_model

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


keyword_list = ['advertising', 'blockchain', 'cloud', 'COVID', 'credit', 'currency exchange',
                'digital', 'election', 'exchange rate', 'growth', 'hack', 'housing market', 'inflation',
                'insurance', 'politic', 'profitability', 'recession',
                'security', 'software', 'supply chain', 'uncertainty', 'war']

#format percentages in query results
def format_percent(value):
    return "{:.0%}".format(value)

def format_dollar(value):
    return "${:.2f}".format(value)


