# import dash
# import dash_bootstrap_components as dbc
#
# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#
# app.layout = dbc.Container(
#     dbc.Alert("Hello Bootstrap!", color="success"),
#     className="p-5",
# )
#
# if __name__ == "__main__":
#     app.run_server()


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


app = Dash(__name__)
app.layout = html.Div(children=[
    dbc.Row(
            [
                # dbc.Col(html.Div([dcc.DatePickerRange(id='date-picker-range',
                #                                   start_date=date(2017, 1, 1),
                #                                   end_date=date(2020, 1, 1))],),
                #     width={"size": 3, "offset": 1}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_symbol_dropdown_list,
                                           placeholder='Choose a Stock',
                                           id='dropdown_input')
                              ],
                             ), width={"size": 3, "offset": 3}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.keyword_dropdown(),
                                           id='keyword_dropdown_input', placeholder='Choose a Keyword')\
                              ],
                             ), width={"size": 2})]
    )])

@app.callback(
    Output('dropdown-output', 'figure'),
    Input('dropdown_input', 'value'),
    Input('keyword_dropdown_input', 'value')
    # [Input('date-picker-range', 'value'), Input('date-picker-range', 'value')]
)
def update_output(dropdown_value):
    edgar_chart = dcc.Graph(
        id='my-date-output',
        figure=my_dash_charts.Edgar_Mult_Y_Axis_Lines(
            dataframes_from_queries.inflation_mention_chart(dropdown_value, '2018-01-01', '2020-01-01'), dropdown_value)
    )
    return edgar_chart
# def update_output(start_date, end_date):
#     edgar_chart = dcc.Graph(
#         id='my-date-output',
#         figure=my_dash_charts.Edgar_Mult_Y_Axis_Lines(
#             dataframes_from_queries.inflation_mention_chart('AAL', start_date, end_date), 'AAL')
#     )
#     return edgar_chart

if __name__ == '__main__':
    app.run_server(debug=True)


import pandas as pd
import passwords
from sqlalchemy import create_engine
# import dataframes_from_queries
# print(dataframes_from_queries.top_keyword_correlations_with_rolling_avg('asc'))
