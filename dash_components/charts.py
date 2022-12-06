from flask import Flask
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import dataframes_from_queries
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import passwords

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()



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


def Edgar_Mult_Y_Axis_Lines(dataframe_input, stock_name, keyword):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"stock_date"], y=dataframe_input.loc[:,"stock_price"], name=stock_name),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"stock_date"],
                   y=dataframe_input.loc[:,f"{keyword} Mentions Rolling Average"], name=f"{keyword} Mention Percentage"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Stock Most Correlated with Keyword Mentions in Public Filings"
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    # Set y-axes titles
    fig.update_yaxes(title_text=f"<b>{stock_name}</b> Closing Price", secondary_y=False)
    fig.update_yaxes(title_text=f"<b>{keyword}</b> Count", secondary_y=True)

    return fig


def generate_table(dataframe):
    table = dbc.Table.from_dataframe(dataframe, striped=True, bordered=True, hover=True)
    return table

