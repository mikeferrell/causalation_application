import dash.exceptions
import dash
from flask import Flask
from dash import Dash, dcc, html, Input, Output, State, exceptions
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
import assets.sidebar as sidebar

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()

# duplicate queries from df_from_queries file
# top_correlated_coin_and_stock_data_frame = pd.read_sql(dataframes_from_queries.top_correlated_coin_and_stock,
#                                                        con=connect)
# top_stock_and_coin_close_prices_over_time_data_frame = pd.read_sql(
#     dataframes_from_queries.top_stock_and_coin_close_prices_over_time, con=connect)


app = Dash(__name__, use_pages=True, title='Causalation', serve_locally=False, external_stylesheets=[dbc.themes.LITERA])
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

# navbar = dbc.Navbar(
#     dbc.Container(
#         [
#             html.A(
#                 # Use row and col to control vertical alignment of logo / brand
#                 dbc.Row(
#                     [
#                         dbc.Col(html.Img(src=small_logo_image, height="30px")),
#                         dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
#                     ],
#                     align="center",
#                     className="g-0",
#                 ),
#                 href="/",
#                 style={"textDecoration": "none"},
#             ),
#             dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
#         ]
#     ),
#     color="dark",
#     dark=True,
# )


# navbar = dbc.NavbarSimple(
#     children=[
#         dbc.Container([
#             html.A(
#                 dbc.Row(
#                     [
#                         dbc.Col(html.Img(src=small_logo_image, height="30px")),
#                         dbc.Col(dbc.NavItem(dbc.NavLink("Dashboard", href="/"))),
#                         dbc.Col(dbc.NavItem(dbc.NavLink("About", href="/about"))),
#                         dbc.Col(dbc.NavItem(dbc.NavLink("Contact", href="/contact"))),
#                     ],
#                     align="left",
#                     className="g-0",
#                 )
#             )
#     ])],
#     brand="Causalation",
#     brand_external_link=True,
#     brand_href="/",
#     color="primary",
#     dark=True,
#     fluid=True,
#     expand='lg',
#     sticky=True
# )




# html.Div(style={'backgroundColor': colors['background'], 'display': 'inline-block'}, children=[
app.layout = dbc.Container([
    # dbc.Row(dbc.Col(html.Div(navbar))),
    dbc.Row(dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_logo.decode()),
                                      style={'height': '5%', 'width': '70%'})),
                    width={"size": 6, "offset": 3})),
    dbc.Row(dbc.Col(html.Div(html.H4(children='Is it Correlation? Causation? Who knows, I just want to get rich')),
                    width={"size": 8, "offset": 3})),
    dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
    dbc.Row(dbc.Col(dash.page_container)),
]
)


#
# @server.route("/")
# def my_dash_app():
#     return app.index()



if __name__ == '__main__':
    application.run(port=8080, debug=True)
