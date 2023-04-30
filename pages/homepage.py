import dash
from dash import html, Input, Output, callback
import dash_bootstrap_components as dbc
from static.color_palette import colors

dash.register_page(__name__, path='/', name="Home")
logo_image_direct = 'static/causalation-logo-no-background.png'


layout = dbc.Container([
    dbc.Row(dbc.Col([html.Div([
                        html.P(''''''),
                        html.H2(children='''Is it Correlation? Causation? Let's find out.''',
                                     style={'textAlign': 'center'}),
                        html.P(children='''Causalation allows you to explore the 
                              relationship between stocks and SEC filings.''',
                                     style={'textAlign': 'center'})
                               ],
                    # className="h-100 p-5 text-white bg-dark rounded-3",
                    ),])),
                    # style={'color': colors["background"],
                    #     'background-color': colors["dark_theme"]}
    dbc.Row([
        dbc.Col(
            html.Div([
                html.P(''''''),
                dbc.NavLink(dbc.Button("Explore Historical Data", size="lg", id="dashboard-button", className="me-1",
                                       style={"backgroundColor": colors["dark_theme"], "color": colors["background"]}),
                            href="/dashboard", ),
            ],
                style={'textAlign': 'center'},
            ),
            width={"size": 4}
        ),
        dbc.Col(
            html.Div([
                html.P(''''''),
                html.H4(
                    children='First Time Here?',
                    style={
                        'textAlign': 'center'
                    }),
                html.P(''''''),
                dbc.NavLink(dbc.Button("Learn More About the Data", size="lg", id="about-button",
                                       className="me-1", style={"backgroundColor": colors["red_button"],
                                                                "color": colors["background"]}),
                            href="/about"),
            ],
                style={'textAlign': 'center'},
                # "backgroundColor": colors["light_theme"], "height": "100%"
            ),
            width={"size": 4}, ),
        dbc.Col(
            html.Div([
                html.P(''''''),
                dbc.NavLink(dbc.Button("See Future Predictions", size="lg", id="prediction-button", className="me-1",
                                       style={"backgroundColor": colors["dark_theme"], "color": colors["background"]}),
                            href="/predictions", ),
            ],
                style={'textAlign': 'center'},
            ),
            width={"size": 4}
        ),
    ],)
],
)

@callback(
    Output("button-output", "children"),
    [Input("dashboard-button", "n_clicks"),
    Input("prediction-button", "n_clicks"),
    Input("about-button", "n_clicks")]

)
def on_button_click(n):
    if n is None:
        return "Not clicked."
    else:
        return f"Clicked {n} times."
