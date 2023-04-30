from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from static.color_palette import colors
import base64

small_logo_image_direct = 'static/small_logo.png'

# SIDEBAR_STYLE = {
#     "position": "fixed",
#     "top": 0,
#     "left": 0,
#     "bottom": 0,
#     "width": "10rem",
#     "padding": "2rem 1rem",
#     "background-color": "#f8f9fa"
# }
#
# # the styles for the main content position it to the right of the sidebar and
# # add some padding.
# CONTENT_STYLE = {
#     "margin-left": "18rem",
#     "margin-right": "2rem",
#     "padding": "2rem 1rem"
# }
#
# sidebar = html.Div(
#     [
#         html.Img(src=small_logo_image_direct,
#                  style={'height': '15%', 'width': '95%'}),
#         html.Hr(),
#         html.P(
#             "Causalation", className="lead"
#         ),
#         dbc.Nav(
#             [
#                 dbc.NavLink("Home", href="/", active="exact"),
#                 dbc.NavLink("ML Modeling", href="/predictions", active="exact"),
#                 dbc.NavLink("Dashboard", href="/dashboard", active="exact"),
#                 dbc.NavLink("Blog", href="/blog", active="exact"),
#                 dbc.NavLink("About", href="/about", active="exact"),
#                 dbc.NavLink("Contact", href="/contact", active="exact")
#             ],
#             vertical=True,
#             pills=True,
#         ),
#     ],
#     style=SIDEBAR_STYLE,
# )
#
# content = html.Div(id="page-content", style=CONTENT_STYLE)

NAVBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "right": 0,
    "padding": "1rem",
    "background-color": colors['dark_theme']
}

CONTENT_STYLE = {
    "margin-top": "5rem",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"
}

nav_items = dbc.Nav(
                 [
                 dbc.NavItem(dbc.NavLink("Home", href="/", active="exact",
                                         style={"color": colors['background']})),
                          dbc.NavItem(dbc.NavLink("AI Predictions", href="/predictions", active="exact",
                                                  style={"color": colors['background']})),
                          dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", active="exact",
                                                  style={"color": colors['background']})),
                          dbc.NavItem(dbc.NavLink("Blog", href="/blog", active="exact",
                                                  style={"color": colors['background']})),
                          dbc.NavItem(dbc.NavLink("About", href="/about", active="exact",
                                                  style={"color": colors['background']})),
                          dbc.NavItem(dbc.NavLink("Contact", href="/contact", active="exact",
                                                  style={"color": colors['background']}))
                          ],
            className="ml-auto",
            navbar=True
        ),

navbar = dbc.Navbar(dbc.Container(
    [
        html.Img(src=small_logo_image_direct,
                      style={'height': '8vh', 'width': 'auto'}),
        dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
        dbc.Collapse(
            nav_items,
            id="navbar-collapse",
            is_open=False,
            navbar=True)
    ],),
    color=colors['dark_theme'],
    dark=False,
    style=NAVBAR_STYLE,
    className="navbar-expand-lg"
)

sidebar = html.Div()

content = html.Div(id="page-content", style=CONTENT_STYLE)

@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open
