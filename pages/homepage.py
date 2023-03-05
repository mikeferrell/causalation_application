import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name="Home")

colors = {
    'background': '#D3D3D3',
    'text': '#00008B',
    'red_button': '#A52A2A'
}


layout = dbc.Container([
    dbc.Row(dbc.Col(html.Div(html.H3(children='''Is it Correlation? Causation? Let's find out.''',
                                     style={'textAlign': 'center'})),
                    width={"size": 8, "offset": 2})),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''Causalation allows you to explore the relationship between stocks and SEC filings.'''),
        html.P(''''''),
                ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div(
            [html.P(''''''),
             dbc.NavLink(dbc.Button("See Stock Predictions", size="lg", id="prediction-button", className="me-1"),
                         href="/predictions"),
             ]),
                style={'textAlign': 'center'},
                width={"size": 8, "offset": 2},
                )
    ),
    html.Div(html.H2(
        children='',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(dbc.Button("Explore the Data", size="lg", id="dashboard-button", className="me-1"),
                                  href="/dashboard"),
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    html.Div([html.P(''''''),
              html.H4(
        children='First Time Here?',
        style={
            'textAlign': 'center'
        }),
              html.P('''''')]
    ),
    dbc.Row(
        dbc.Col(
            html.Div([dbc.NavLink(dbc.Button("Learn More About the Data", size="lg", id="about-button",
                                             className="me-1", color="warning"),
                                  href="/about"),
                      ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
            )
    ),
])

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