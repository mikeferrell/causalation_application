import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import images as my_images
import base64

dash.register_page(__name__, path='/about')

screenshot_helper = 'static/causalation_how_to.png'
colors = {
    'background': '#D3D3D3',
    'text': '#000000'
}



layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            html.H6(dcc.Markdown('''**DISCMLAIMER**: This is not financial advice, this is just a project to make SEC
            data more accessible. What you do with that data is up to you. Any "recommendations" are simply machine 
            learning results based on the underlying data, and not actual financial recommendations.
            '''))
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''FAQ''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''So what exactly am I looking at here?''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
        html.P('''Causalation is a way to spot correlations between stock prices and what companies are discussing in their public filings.'''),
        html.P(
                '''The dashboard is bringing together keywords extracted from 10-K & 10-Q filings
                with weekly stock closings from S&P 500 companies (and some meme stocks) over the same time period.'''),
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''What is on the Dashboard?''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.Img(src=screenshot_helper,
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
            **1:** Filter by Stock
            
            **2:** Filter by Date
            
            **3:** Filter by number of week delay. This allows you to correlate stocks with topics mentioned X number 
            of weeks ago
            
            **4:** Filter by Filing Type. Only 10-K's available today
            
            **5:** Filter by keywords mentioned. Each keyword includes all larger words. e.g. "cloud computing" would 
            be captured by "cloud"
            
            **6:** Apply filers. Only click it once, it's pretty slow for now
            
            **7:** This chart shows each stock's opening price for given week and the percentage of SEC Filings that 
            mention the topic select. The topic selected is cohorted by week and the percentage represented in the chart 
            is based on a 12 week rolling average
            
            **8:** Total number of times this keyword is mentioned within the timeframe selected
            
            **9:** The correlation ratio between the stock and the keyword selected, within the given filters
            
            **10:** Regardless of the stock you selected, this table shows the top 10 stocks most correlated with the 
            keyword selected; within the filters applied
                
            **11:** This table is the same as #10, but ordered by stocks inversely correlated with the selected keyword
            '''),
        ]),
            style={'textAlign': 'left'},
            width={"size": 6, "offset": 3},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''How is the public filing data normalized?''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.P(
                '''The data is pulled from SEC public filings. Text is then extracted from the sections 
                4 "Risk Factors" and 7 "Management’s Discussion and Analysis of Financial Condition and Results of Operations"''')
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H3('''Why isn't the start date what I selected?''', className="text-muted")
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.P(
                '''The chart includes the 12 week rolling average of keyword mentions- this ensures that a slow week
                in filings doesn't distort the data. But to ensure that the first few weeks also aren't dramatic swings,
                the first 6 datapoints are disregarded.''')
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
])

