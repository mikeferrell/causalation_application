import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/blog_pages/5_14_23_blog')

performance_screenshot = '../static/blog_images/performance_week_of_5_8_23.png'
buy_screenshot = '../static/blog_images/buys_for_5_8_23.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000',
    'nav': '#0000FF'
}

layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''5/14/23''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            dcc.Markdown('''
            The site is now operational, so I'll revert my focus to making some model improvements in the coming weeks.
             Let's take a look at how it performed last week and see what's broken this time. 
             
             Here are the buy recommendations for this past Monday: '''),
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
            dcc.Markdown('''And here are the performance results: ''')
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
            As we can see, we edged out a slight profit of 0.269%, which has a CAGR of 14.05%- not bad. Unfortunately, this
            likely would have been about break even if we factored in transactions costs. This strategy keeps 
            transaction costs low because it's long only, stocks only, and no leverage. That means most trading platforms
            will give you commission free trades so the only cost will be the bid-ask spread on these stocks, all of
             which have high liquidity. Even with such a thin margin here though, those low costs are still too much.
            
            So what happened when we look more closely at the results? We can see the biggest loss, about 1% of the 
            principal, Was TSN (Tyson Foods) which dropped from $54.42 to $49.34. What's more dramatic though is that
            the Friday closing price was $60.13, so this stock had already dropped 10% between it's selection and our
            "purchase". This is the opposite of last week where there was some price slippage over the weekend eating 
            into returns, if this drop had occurred after Monday's open then we would have been crushed.
            
            TSN moved so dramatically over the weekend because their earnings were unexpectedly awful. Considering that
            earnings reports can have a dramatic influence on stocks up or down, maybe it would be prudent to exclude
            any stock from purchase who is reporting earnings this week. This model is meant to follow momentum and not
            predict individual company success/failure. I'll add this idea to the backlog.
            '''),
            dcc.Markdown(''' 
            **What's Next** 
            
            Here are the current outstanding improvements that can be made to the model. 
            
            **1.** Add inversely correlated relationships to the model
            
            **2.** Expand it from top 10 relationships, to top 20 or 30; allowing for more options to buy each week
            
            **3.** Surpress any company reporting earnings that week
            
            **4.** Revisit the keyword list to delete low value words and introduce more that are relevant to current 
            market trends
            
            **5.** Add commodity and industry ETFs to the stock list
            
            **6.** After making these changes, start a new paper trading process with a principal of $10,000 and use the
            compounding results instead of resetting the principal each week. 
            
            **7.** The backtest is also out of date, so that will need to be rerun after making these changes
            
            Stay tuned to see if these changes help!
            
            
            '''),

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

