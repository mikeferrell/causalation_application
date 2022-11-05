import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', name="Home")

colors = {
    'background': '#D3D3D3',
    'text': '#00008B'
}


layout = dbc.Container([
    dbc.Row(dbc.Col(html.Div(html.H4(children='Is it Correlation? Causation? Who knows, I just want some alpha',
                                     style={'textAlign': 'center'})),
                    width={"size": 8, "offset": 2})),
    dbc.Row(
        dbc.Col(html.Div([
            html.P('''''')
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''Causalation allows you to explore the correlation between stocks and topics mentioned in SEC public
        filings''')
                ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(dbc.Button("Go to Dashboard", size="lg", id="dashboard-button", className="me-1"),
                                  href="/dashboard"),
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),

])

@callback(
    Output("button-output", "children"), [Input("dashboard-button", "n_clicks")]
)
def on_button_click(n):
    if n is None:
        return "Not clicked."
    else:
        return f"Clicked {n} times."