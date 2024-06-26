import dash
from dash import html
import dash_bootstrap_components as dbc
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/contact')



layout = dbc.Container([
    # image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'height': '2%', 'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ]),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

    dbc.Row(
                dbc.Col(html.Div([
                html.H6('''Is there more data you want to see here? Email us and let us know what charts or datasets to add!''')
                        ]),
                    style={'textAlign': 'center', 'fontWeight': '400',},
                    width={"size": 8, "offset": 2},
                ),
        className="p-3"
            ),
            dbc.Row(
                dbc.Col(html.Div([
                    html.H3('''causalation@gmail.com''')
                ]),
                    style={'textAlign': 'center','color': colors['dark_theme']},
                    width={"size": 8, "offset": 2}
                )
            ),
    dbc.Row(html.Div([html.Hr(className="my-2"),
                      html.H1("")],
                     style={'padding': 15}),
            className="h-10"),
])

