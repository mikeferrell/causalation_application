from flask import Flask
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import date
import dataframes_from_queries
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import passwords
import dash_components.charts as my_dash_charts
import assets.images as my_images
import base64

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

# duplicate queries from df_from_queries file
top_correlated_coin_and_stock_data_frame = pd.read_sql(dataframes_from_queries.top_correlated_coin_and_stock,
                                                       con=connect)
top_stock_and_coin_close_prices_over_time_data_frame = pd.read_sql(
    dataframes_from_queries.top_stock_and_coin_close_prices_over_time, con=connect)

app = Dash(__name__, title='Causalation', serve_locally=False, external_stylesheets=[dbc.themes.LITERA])
server = Flask(__name__)
application = app.server

logo_image = my_images.logo
small_logo_image = my_images.small_logo
encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "10rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.Img(src='data:image/png;base64,{}'.format(encoded_small_logo.decode()),
                 style={'height': '15%', 'width': '95%'}),
        html.Hr(),
        html.P(
            "A simple sidebar layout with navigation links", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/", active="exact"),
                dbc.NavLink("About", href="/about", active="exact"),
                dbc.NavLink("Contact", href="/contact", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

# html.Div(style={'backgroundColor': colors['background'], 'display': 'inline-block'}, children=[
app.layout = html.Div(children=[
    dbc.Row(dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_logo.decode()),
                                      style={'height': '5%', 'width': '70%'})),
                             width={"size": 6, "offset": 3})),
    dbc.Row(dbc.Col(html.Div(html.H4(children='Is it Correlation? Causation? Who knows, I just want to get rich')),
                    width={"size": 8, "offset": 3})),
    dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar, content]), width=6)),
    dbc.Row(
        [
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_symbol_dropdown_list,
                                           id='dropdown-input', placeholder='Choose a Stock'),
                              html.Div(id='dropdown-output')
                              ],
                             ), width={"size": 3, "offset": 3}),
            dbc.Col(html.Div([dcc.DatePickerRange(id='date-picker-range',
                                                  start_date=date(2017, 1, 1),
                                                  end_date=date(2022, 8, 1)),
                              html.Div(id='my-date-output')], ),
                    width={"size": 3, "offset": 1})
            ]
    ),
    html.Div(html.H1(
        children='Static Charts',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        [
            dbc.Col(my_dash_charts.generate_table(
                dataframes_from_queries.top_inflation_correlations_with_rolling_avg('desc')),
                width={"size": 3, "offset": 3}),
            dbc.Col(my_dash_charts.generate_table(
                dataframes_from_queries.top_inflation_correlations_with_rolling_avg('asc')),
                width={"size": 3, "offset": 1}),
        ]
    )
])

# html.Div([dcc.Location(id="url"), sidebar, content]),



# html.Div(html.H4(children='Stocks Correlated with Inflation Mentions'),

#
# html.H4(children='Stocks Inversely Correlated with Inflation Mentions'),
#     my_dash_charts.generate_table(dataframes_from_queries.top_inflation_correlations_with_rolling_avg('asc')),
#
# dcc.Graph(
#     id='example-graph-2',
#     figure=my_dash_charts.Mult_Y_Axis_Lines(top_stock_and_coin_close_prices_over_time_data_frame, "TFC")
# ),
#
# html.H4(children='Most Correlated Stock and Crypto'),
#     my_dash_charts.generate_table(top_correlated_coin_and_stock_data_frame),
#
# html.H3(children='Crypto and Stock Top 100 Correlations'),
#     my_dash_charts.generate_table(dataframes_from_queries.correlation_data_frame)
# ])

@server.route("/")
def my_dash_app():
    return app.index()


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname == "/":
        return html.P("Causalation")
    elif pathname == "/about":
        return html.P("This is the content of page 1. Yay!")
    elif pathname == "/contact":
        return html.P("Oh cool, this is page 2!")
    # If the user tries to reach a different page, return a 404 message
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3",
    )


# button = html.Div(
#     [
#         dbc.Button(
#             "Click me", id="example-button", className="me-2", n_clicks=0
#         ),
#         html.Span(id="example-output", style={"verticalAlign": "middle"}),
#     ]
# )
#
#
# @app.callback(
#     Output("example-output", "children"), [Input("example-button", "n_clicks")]
# )
# def on_button_click(n):
#     if n is None:
#         return "Not clicked."
#     else:
#         return f"Clicked {n} times."


@app.callback(
    Output('dropdown-output', 'children'),
    Output("my-date-output", "children"),
    Input('dropdown-input', 'value'),
    [Input("date-picker-range", "start_date"), Input("date-picker-range", "end_date")]
)
def update_output(value, start_date, end_date):
    start_date = str(start_date)
    end_date = str(end_date)
    description = 'Strongest Crypto Correlation Based on Stock Selection'
    dropdown_table = my_dash_charts.generate_table(dataframes_from_queries.stock_crypto_correlation_filtered(value))
    # crypto_in_chart = dataframes_from_queries.stock_crypto_correlation_filtered(value)['coin_name'].iloc[0]
    # new_chart = dcc.Graph(
    #     id='example-graph-2',
    #     figure=my_dash_charts.Mult_Y_Axis_Lines(dataframes_from_queries.change_stock_on_chart(value), value)
    #     )
    # edgar_dropdown_table = my_dash_charts.generate_table(dataframes_from_queries.inflation_mention_correlation(value))
    edgar_chart = dcc.Graph(
        id='example-graph-2',
        figure=my_dash_charts.Edgar_Mult_Y_Axis_Lines(
            dataframes_from_queries.inflation_mention_chart(value, start_date, end_date), value)
    )
    return description, dropdown_table, edgar_chart
    # , new_chart, edgar_dropdown_table, edgar_chart


if __name__ == '__main__':
    application.run(debug=True)
