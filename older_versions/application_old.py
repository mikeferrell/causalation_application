from flask import Flask
from dash import Dash, dcc, html, Input, Output
import pandas as pd
from ml_models import dataframes_from_queries
from sqlalchemy import create_engine
import passwords
import dash_components.charts as my_dash_charts

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

#duplicate queries from df_from_queries file
top_correlated_coin_and_stock_data_frame = pd.read_sql(dataframes_from_queries.top_correlated_coin_and_stock, con=connect)
top_stock_and_coin_close_prices_over_time_data_frame = pd.read_sql(
dataframes_from_queries.top_stock_and_coin_close_prices_over_time, con=connect)


app = Dash(__name__, title='Causalation')
server = Flask(__name__)
application = app.server


colors = {
'background': '#FFFFFF',
'text': '#000000'
}



app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
html.H1(
    children='Causalation',
    style={
        'textAlign': 'center',
        'color': colors['text']
    }
),

html.Div([
    dcc.Dropdown(dataframes_from_queries.stock_symbol_dropdown_list, id='dropdown-input', placeholder ='Choose a Stock'),
    html.Div(id='dropdown-output')
]),

html.H1(
    children='Static Charts',
    style={
        'textAlign': 'center',
        'color': colors['text']
    }),

html.H4(children='Stocks Correlated with Inflation Mentions'),
    my_dash_charts.generate_table(dataframes_from_queries.top_keyword_correlations_with_rolling_avg('desc')),

html.H4(children='Stocks Inversely Correlated with Inflation Mentions'),
    my_dash_charts.generate_table(dataframes_from_queries.top_keyword_correlations_with_rolling_avg('asc')),

dcc.Graph(
    id='example-graph-2',
    figure=my_dash_charts.Mult_Y_Axis_Lines(top_stock_and_coin_close_prices_over_time_data_frame, "TFC")
),

html.H4(children='Most Correlated Stock and Crypto'),
    my_dash_charts.generate_table(top_correlated_coin_and_stock_data_frame),

html.H3(children='Crypto and Stock Top 100 Correlations'),
    my_dash_charts.generate_table(dataframes_from_queries.correlation_data_frame)
])

@server.route("/")
def my_dash_app():
    return app.index()

@app.callback(
    Output('dropdown-output', 'children'),
    Input('dropdown-input', 'value')
)
def update_output(value):
    description = 'Strongest Crypto Correlation Based on Stock Selection'
    dropdown_table = my_dash_charts.generate_table(dataframes_from_queries.stock_crypto_correlation_filtered(value))
    # crypto_in_chart = dataframes_from_queries.stock_crypto_correlation_filtered(value)['coin_name'].iloc[0]
    new_chart = dcc.Graph(
        id='example-graph-2',
        figure=my_dash_charts.Mult_Y_Axis_Lines(dataframes_from_queries.change_stock_on_chart(value), value)
        )
    edgar_dropdown_table = my_dash_charts.generate_table(dataframes_from_queries.inflation_mention_correlation(value))
    edgar_chart = dcc.Graph(
        id='example-graph-2',
        figure=my_dash_charts.Edgar_Mult_Y_Axis_Lines(dataframes_from_queries.inflation_mention_chart(value), value)
        )
    return description, dropdown_table, new_chart, edgar_dropdown_table, edgar_chart


if __name__ == '__main__':
    application.run(debug=True)

