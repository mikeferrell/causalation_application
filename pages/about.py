import dash.exceptions
import dash
from flask import Flask
from dash import Dash, dcc, html, Input, Output, State, exceptions, callback
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

dash.register_page(__name__, path='/about')

colors = {
    'background': '#D3D3D3',
    'text': '#000000'
}

logo_image = my_images.logo
small_logo_image = my_images.small_logo
encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())


layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''FAQ''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''So what exactly am I looking at here?''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''Causalation is a way to spot correlations between stock prices and what companies are discussing in their public filings.''')
                ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.P(
                '''The dashboard is bringing together weekly stock closes from S&P 500 companies- as well as a few popular meme stocks-
                with keywords extracted from 10-K and 10-Q filings over the same time period.''')
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''So how is the public filing data normalized''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.P(
                '''The data is pulled from SEC public filings. Text is then extracted from the sections 
                4 "Risk Factors" and 7 "Management’s Discussion and Analysis of Financial Condition and Results of Operations"''')
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
])

