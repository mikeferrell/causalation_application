from dash import html
import dash_bootstrap_components as dbc
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
    "background-color": "#71797E"
}

CONTENT_STYLE = {
    "margin-top": "5rem",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"
}

navbar = dbc.Navbar(
    [
        html.Img(src=small_logo_image_direct,
                      style={'height': '8vh', 'width': 'auto'}),
             dbc.Nav(
                 [
                 dbc.NavItem(dbc.NavLink("Home", href="/", active="exact")),
                          dbc.NavItem(dbc.NavLink("ML Modeling", href="/predictions", active="exact")),
                          dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard", active="exact")),
                          dbc.NavItem(dbc.NavLink("Blog", href="/blog", active="exact")),
                          dbc.NavItem(dbc.NavLink("About", href="/about", active="exact")),
                          dbc.NavItem(dbc.NavLink("Contact", href="/contact", active="exact"))
                          ],
            className="ml-auto",
            navbar=True
        ),
    ],
    color="light",
    dark=False,
    style=NAVBAR_STYLE,
)

sidebar = html.Div()

content = html.Div(id="page-content", style=CONTENT_STYLE)
