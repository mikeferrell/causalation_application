import dash
from dash import html
import dash_bootstrap_components as dbc
import images as my_images
import base64

dash.register_page(__name__, path='/blog_pages/2_12_23_blog')

screenshot_helper = 'static/causalation_how_to.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}



layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''2/13/23''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''Ok, first update here. If you're reading this then either you've somehow stumbled across my 
        unfinished website...or you know me and I told you about it. Hi!'''),
        html.P('''I'm still building, so don't expect much for concrete updates. Also, I'll delete this post once
        I actually have something to say about the ML model I'm building.'''),
        html.P('''Stay Tuned :)'''),
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(
                )
    ),
])

