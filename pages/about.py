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
    'text': '#00008B'
}

logo_image = my_images.logo
small_logo_image = my_images.small_logo
encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())


layout = dbc.Container([
    html.Div(html.H1(
        children='Top Stock Correlations',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }))
])

