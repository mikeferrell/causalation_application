import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/blog_pages/3_5_23_blog')

buy_screenshot = '../static/blog_images/buys_for_3_6_23.png'
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
            meantime, let's see what would happen. This assumes I'll be to purchase fractional shares, so I'll need to 
            setup a Robinhood account for this experiment.
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
        **Things that need to be fixed for before next week:**
        
        **1.** Ensure the regression model has no gaps in training data, which is likely what's causing the forecasted 
        price jumps. There are other model improvements to roll out in subsequent weeks, but this is the first to fix.
        
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

