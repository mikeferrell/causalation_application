from dash import html
import dash_bootstrap_components as dbc
import assets.images as my_images
import base64

logo_image = my_images.logo
small_logo_image = my_images.small_logo
encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())

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
            "Causalation", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Dashboard", href="/", active="exact"),
                dbc.NavLink("About", href="/about", active="exact"),
                dbc.NavLink("Contact", href="/contact", active="exact")
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)