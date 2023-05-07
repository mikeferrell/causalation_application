import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/blog_pages/5_7_23_blog')

performance_screenshot = '../static/blog_images/performance_week_of_5_1_23.png'
buy_screenshot = '../static/blog_images/buys_for_5_1_23.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}

layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''5/7/23''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            dcc.Markdown('''
            We're back in action here after doing a lot of work under the hood. At this point, I feel that the model is 
            at a solid MVP status. Since my last post, I have: '''),
            dcc.Markdown('''
            **1.** Updated the backtest to work accurately without any look ahead bias
            
            **2.** Refined the model to train with a cleaner dataset with less entropy introduced
            
            **3.** Setup other calculations such as the Sharpe Ratio and returns to track success
            
            **4.** Improved the way to calculate the share purchase process
            
            There is still quite a bit to do before I will deploy real capital instead of doing this real-time paper
            trading analysis. Let's look at last week's performance to see why:
            
            
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
            Only one stock out of the top 10 most correlated stocks was predicted to rise this week, causing some
            concentration risk. In order to prevent this in future weeks, I'll need to add more stocks and commodity 
            ETFs (such as gold) as mentioned in a previous post. I should also include the top 10 inversely correlated 
            stocks. I think these two changes would reduce concentration risk, as well as make the model more robust in 
            a down market.
            
            Another issue last week is the slippage that occurred from Friday's market close to Monday's market open.
            There isn't a way to solve this without lookahead bias, though I can introduce some measures to track the
            slippage and adjust the strategy for when it occurs.
            
            As a result, we saw a loss of 0.357% last week, instead of the predicted gain of 2.885%.
    ''')
        ]),
            style={'textAlign': 'left'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.Img(src=performance_screenshot,
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
            I'll be working on the site itself this next week, so there won't be any changes to the model. However,
            I expect to continue to track the performance so stay tuned!
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

