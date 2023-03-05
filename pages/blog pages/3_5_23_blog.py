import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import images as my_images
import base64

dash.register_page(__name__, path='/blog_pages/3_5_23_blog')

buy_screenshot = '../static/buys_for_3_6_23.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}



layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''3/5/23''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        dcc.Markdown('''
            This week is the first dry run of buy recommendations. The recommendations are now live on the ML dashboard,
            however every stock is predicted to skyrocket. So we'll wait a week before starting the process, but in the 
            meantime, let's see what would happen.
        ''')
        ]),
            style={'textAlign': 'left'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.Img(src=buy_screenshot,
                     style={'height': '5%', 'width': '80%'}),
            html.P()
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            dcc.Markdown('''
        **Next time**, we'll need to also propose how to split the buys, consistent with the backtest. That means: the higher
        the predicted growth, the higher percentage of the principal that should be allocated to that stock.
        
        Other things that need to be fixed:
        
        **1.** Ensure the regression model has no gaps, which is likely what's causing the forecasted price jumps.
        
        **2.** Ensure the dashboard is more legible. 
        
        **3.** the "Buy Date" column is hard coded for one week in the future, which doesn't account for holidays. Fix that.
    ''')
        ]),
            style={'textAlign': 'left'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(
                )
    ),
])

