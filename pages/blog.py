import dash
from dash import html
import dash_bootstrap_components as dbc
import images as my_images
import base64

dash.register_page(__name__, path='/blog')

screenshot_helper = 'static/causalation_how_to.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}



layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''Blog''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''Follow along as I improve the model 
            and attempt to beat the market by blindly trusting it's recommendations''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''My Thesis: By pulling together public data sources and making them searchable, 
        I can make market data more accessible to everyday traders. And if I use this data effectively, 
        I can develop trading strategies for myself.'''),
        html.P(
                '''My Current Hypothesis: SEC Filings contain language in the sections about risk that are meant to be 
                boiler plate and broad. However, when you assess the trends over time of companies deciding these 
                warnings are/aren't necessary, you can accurately predict the directional movement of stocks that are 
                strongly correlated to broad market shifts.'''),
            html.P(
                '''Follow along in these blog posts to see how the model changes over time and whether or not
                the recommendations are profitable'''),
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 3/5/2023"),
                                      href="/blog_pages/3_5_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['nav']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 2/18/2023"),
                                      href="/blog_pages/2_18_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['nav']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 2/13/2023"),
                                      href="/blog_pages/2_12_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['nav']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
])

