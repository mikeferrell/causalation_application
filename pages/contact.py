import dash
from dash import html
import dash_bootstrap_components as dbc

import assets.images as my_images
import base64

dash.register_page(__name__, path='/contact')

colors = {
    'background': '#D3D3D3',
    'text': '#00008B'
}

logo_image = my_images.logo
small_logo_image = my_images.small_logo
encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())


layout = dbc.Container([
            dbc.Row(
                dbc.Col(html.Div([
                html.P('''Is there more data you want to see here? Email us and let us know what charts or datasets to add!''',
                        className="text-primary")
                        ]),
                    style={'textAlign': 'center'},
                    width={"size": 8, "offset": 2},
                )
            ),
            dbc.Row(
                dbc.Col(html.Div([
                    html.H3('''causalation@gmail.com''', className="text-muted")
                ]),
                    style={'textAlign': 'center','color': colors['text']},
                    width={"size": 8, "offset": 2}
                )
            ),
])

