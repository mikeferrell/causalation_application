from flask import Flask
from dash import Dash, dcc, html
import pandas as pd
from ml_models import dataframes_from_queries
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



# app = Dash(__name__)
server = Flask(__name__)
app = Dash(
    __name__,
    server=server,
    url_base_pathname='/'
)


colors = {
'background': '#FFFFFF',
'text': '#000000'
}


ticker_data_frame = dataframes_from_queries.ticker_data_frame
correlation_data_frame = dataframes_from_queries.correlation_data_frame
# top_correlated_coin_and_stock_data_frame = dataframes_from_queries.top_correlated_coin_and_stock_data_frame
# top_stock_and_coin_close_prices_over_time_data_frame = dataframes_from_queries.top_stock_and_coin_close_prices_over_time_data_frame




def Mult_Y_Axis_Lines(dataframe_input):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"close_date"], y=dataframe_input.loc[:,"close_price"], name="TFC"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"close_date"], y=dataframe_input.loc[:,"coin_price"], name="Ripple"),
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


# df = dataframe_input
#
# trace1 = go.Scatter(x=df['stock_symbol'],
#                     y=df['close_price'],
#                     name='Stock Price',
#                     mode='lines+markers',
#                     yaxis='y1')
# trace2 = go.Scatter(x=df['stock_symbol'],
#                     y=df['coin_price'],
#                     name='Coin Price',
#                     mode='lines+markers',
#                     yaxis='y2')
# data = [trace1, trace2]
# layout = go.Layout(title='Coin and Stock Price over Time',
#                    yaxis=dict(title='stock price'),
#                    yaxis2=dict(title='coin price',
#                                overlaying='y',
#                                side='right'))
# return go.Figure(data=data, layout=layout)


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

html.Div(children='Is it Correlation? Is it Causal? How would I know?', style={
    'textAlign': 'center',
    'color': colors['text']
}),

dcc.Graph(
    id='example-graph-2',
    figure=Mult_Y_Axis_Lines(top_stock_and_coin_close_prices_over_time_data_frame)
),

# html.H4('stock and coin correlation over time'),
# Mult_Y_Axis_Lines(top_stock_and_coin_close_prices_over_time_data_frame),

html.H4(children='Most Correlated Stock and Crypto'),
generate_table(top_correlated_coin_and_stock_data_frame),

html.H3(children='Crypto and Stock Top 100 Correlations'),
generate_table(correlation_data_frame)
])

@server.route("/")
def my_dash_app():
    return app.index()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
