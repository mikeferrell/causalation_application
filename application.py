from flask import Flask
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import dataframes_from_queries
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import passwords

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

#duplicate queries from df_from_queries file
top_correlated_coin_and_stock_data_frame = pd.read_sql(dataframes_from_queries.top_correlated_coin_and_stock, con=connect)
top_stock_and_coin_close_prices_over_time_data_frame = pd.read_sql(
dataframes_from_queries.top_stock_and_coin_close_prices_over_time, con=connect)


app = Dash(__name__)
server = Flask(__name__)
application = app.server


colors = {
'background': '#FFFFFF',
'text': '#000000'
}


ticker_data_frame = dataframes_from_queries.ticker_data_frame
correlation_data_frame = dataframes_from_queries.correlation_data_frame
# top_correlated_coin_and_stock_data_frame = dataframes_from_queries.top_correlated_coin_and_stock_data_frame
# top_stock_and_coin_close_prices_over_time_data_frame = dataframes_from_queries.top_stock_and_coin_close_prices_over_time_data_frame


def Mult_Y_Axis_Lines(dataframe_input, stock_name):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"close_date"], y=dataframe_input.loc[:,"close_price"], name=stock_name),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"close_date"], y=dataframe_input.loc[:,"coin_price"], name="Crypto"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Top Stock and Crypto Correlated with a 1 month Delay"
    )
    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    return fig


def Edgar_Mult_Y_Axis_Lines(dataframe_input, stock_name):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"stock_date"], y=dataframe_input.loc[:,"close_price"], name=stock_name),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"stock_date"], y=dataframe_input.loc[:,"inflation_percentage"], name="Inflation_Mention_Percentage"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Stock Most Correlated with Mentions of Inflations in 10K Filings"
    )
    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    return fig


def generate_table(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ])

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
html.H1(
    children='Causalation',
    style={
        'textAlign': 'center',
        'color': colors['text']
    }
),

html.Div([
    dcc.Dropdown(dataframes_from_queries.dropdown_list, id='dropdown-input', placeholder = 'Choose a Stock'),
    html.Div(id='dropdown-output')
]),

html.H1(
    children='Static Charts',
    style={
        'textAlign': 'center',
        'color': colors['text']
    }),

dcc.Graph(
    id='example-graph-2',
    figure=Mult_Y_Axis_Lines(top_stock_and_coin_close_prices_over_time_data_frame, "TFC")
),

html.H4(children='Most Correlated Stock and Crypto'),
generate_table(top_correlated_coin_and_stock_data_frame),

#trying to make a table with the dropdown value, not working yet
# html.H4(children='Recent Prices'),
# generate_table(dataframes_from_queries.dropdown_results(f'{input_value}')),

html.H3(children='Crypto and Stock Top 100 Correlations'),
generate_table(correlation_data_frame)
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
    dropdown_table = generate_table(dataframes_from_queries.stock_crypto_correlation_filtered(value))
    # crypto_in_chart = dataframes_from_queries.stock_crypto_correlation_filtered(value)['coin_name'].iloc[0]
    new_chart = dcc.Graph(
        id='example-graph-2',
        figure=Mult_Y_Axis_Lines(dataframes_from_queries.change_stock_on_chart(value), value)
        )
    edgar_dropdown_table = generate_table(dataframes_from_queries.inflation_mention_correlation(value))
    edgar_chart = dcc.Graph(
        id='example-graph-2',
        figure=Edgar_Mult_Y_Axis_Lines(dataframes_from_queries.inflation_mention_chart(value), value)
        )
    return description, dropdown_table, new_chart, edgar_dropdown_table, edgar_chart


if __name__ == '__main__':
    application.run(debug=True)

