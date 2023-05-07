import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/blog_pages/3_12_23_blog')

performance_screenshot = '../static/blog_images/performance_week_of_3_6_23.png'
buy_screenshot = '../static/blog_images/buys_for_3_13_23.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}

layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''3/12/23''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            dcc.Markdown('''
            Week one of tracking the model is complete. I'm not yet placing real money down, but I intend to in the
            coming weeks. First, let's see what I need to fix.
            
            I tracked three separate machine learning models, one is a type of linear regression, one is a decision tree
            regressor, and one is a version of a random forest regressor. We'll call them "LR", "DTR", and "RFR" 
            for short. DTR seems to be the most discerning, only recommending we buy 4 stocks that meet our criteria
            while RFR and LR both recommended we buy 9-10 stocks and had some wild expectations of 74-176% gains.
            
            Unfortunately, last week was a no good, very bad for the economy. It was the week of the SVB meltdown, so
            stocks were down across the board. Since DTR was the most conservative, it lost the least money: 9.6%. This
            is compared to the S&P which lost 4.8%.
            
            Here is the data from the DTR model.
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
        **Learnings and Things to Fix:**

        **1.** These models are programmed to only buy stocks and only pick based on strong correlations.
        That means that I'm missing out on inverse correlations and I don't have a way to short the market. This would
        probably work in a bull market, but I'm bearish for the time being. Adding options training seems like a big task,
        but I may want to consider some alternative ways to short the equity markets- maybe tracking different indexes or 
        commodities (gold, etc) instead of just stocks.

        **2.** I'm tracking three ML models, but I'd like to narrow down to one and fine tune it over time. That means
        that I need to backtest these recommendations to pick the best model. In a previous post I mentioned that my
        backtester is "lazy"- I need to fix that. So that will be the priority this week.

        **3.** There is some other housekeeping work to ensure the buy recommendations run smoothly and the results 
        (screenshot above) are generated automatically instead of tracked by hand.
        
        Keep up weekly to see how we improve and if we can beat the market.
        
        Here are the buy recommendations for this next week. A lot of similar stock names, but some new correlations
        have entered the mix. Let's see if the week ahead is better for the market than last week.
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
        dbc.Col(
        )
    ),
])

