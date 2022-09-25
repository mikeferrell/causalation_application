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
            dbc.Col(html.Div([dcc.DatePickerRange(id='date-picker-range',
                                                  start_date=date(2017, 1, 1),
                                                  end_date=date(2020, 1, 1)),
                              html.Div(id='my-date-output')],),
                    width={"size": 3, "offset": 1})
    )])

@app.callback(
    Output("my-date-output", "children"),
    [Input("date-picker-range", "start_date"), Input("date-picker-range", "end_date")]
)
def update_output(start_date, end_date):
    start_date = str(start_date)
    end_date = str(end_date)
    edgar_chart = dcc.Graph(
        id='example-graph-2',
        figure=my_dash_charts.Edgar_Mult_Y_Axis_Lines(
            dataframes_from_queries.inflation_mention_chart('AAL', start_date, end_date), 'AAL')
    )
    return edgar_chart

if __name__ == '__main__':
    app.run_server(debug=True)


import pandas as pd
import passwords
from sqlalchemy import create_engine
# import dataframes_from_queries
# print(dataframes_from_queries.top_inflation_correlations_with_rolling_avg('asc'))
