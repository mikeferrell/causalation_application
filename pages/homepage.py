import dash
from dash import html, Input, Output, callback
import dash_bootstrap_components as dbc
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/', name="Home")


layout = dbc.Container([
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                  style={'height': '70%', 'width': '70%'})),
                width={"size": 5, "offset": 1},
                style={"height": "90%"}),
            dbc.Col(html.Div([
                html.P(''),
                html.H2(children='''Is it Correlation? Causation?''',
                             style={'textAlign': 'center', 'fontWeight': '600'}),
                html.H2(children='''Let's find out?''',
                        style={'textAlign': 'center', 'fontWeight': '600'}),
                       ],
                className='p-5 px-0',
            # className="h-100 p-5 text-white bg-dark rounded-3",
            ), width={"size": 6},
            style={"height": "100%"}),
            ],
        className="p-1 px-0 py-0 pt-0 pb-1"
        ),

    #Buttons
    dbc.Row(html.Div([html.Hr(className="my-2"),
                     html.H1("")],
                     style={'padding': 15}),
            className="h-10"),
    dbc.Row([dbc.Col(html.Div(
                html.H3(children='''Causalation allows you to explore the 
                      relationship between stocks and SEC filings.''',
                    style={'textAlign': 'center', 'fontWeight': '300'}),
            className='p-5 px-0'
                ),
            width={"size": 5, "offset": 1}
                                     ),
        dbc.Col(
            html.Div([
                html.P(''''''),
                dbc.NavLink(dbc.Button("Explore Historical Data", size="lg", id="dashboard-button", className="me-1",
                                       style={"backgroundColor": colors["dark_theme"], "color": colors["background"]}),
                            href="/dashboard", ),
                html.P(''''''),
                dbc.NavLink(dbc.Button("See Future Predictions", size="lg", id="prediction-button", className="me-1",
                                       style={"backgroundColor": colors["dark_theme"], "color": colors["background"]}),
                            href="/predictions", ),
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
            ),
            width={"size": 4, "offset": 1}
        ),
    ],
    className="h-25")
],
style={"height": "100vh"},
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
