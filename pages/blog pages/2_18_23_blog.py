import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import images as my_images
import base64

dash.register_page(__name__, path='/blog_pages/2_18_23_blog')

screenshot_helper = 'static/causalation_how_to.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}



layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''2/18/23''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''Alright, the V1 of the machine learning trading algorithm is complete, and....it sucks!'''),
        html.P('''Well, sort of. This is a "lazy" model. In order to be most accurate to the actual recommendations, each week the 
        new list of top correlated stocks should be selected and then run through the model. However, I used just the most
        recent recommendations which means that older weeks have less and less accurate data for training. Since this
        doesn't affect the accuracy of future predictions, I'm not going to fix it now. Let's just look at the results:'''),
        html.P('''It looks like I was able to convert $1,000 to $555 over the course of 5 months. The S&P 500
        had a bad time over the same period, but it's still unimpressive. The important thing is that I now have
        a functioning model and a way to backtest the model against market performance.'''),
        html.P('''Next, I need to go back and tune it. That means I need to tune the ML model, improve the 
        total data collected, choose different keywords to track, and ensure that I can run this model on more
        recent data. That last one is going to be tricky since the current model works only on data where I already have
        the future market data for X number of weeks in the future.'''),
        html.P('''So lots to work on before this model is ready to be shared.'''),
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

