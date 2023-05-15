import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/about')


layout = dbc.Container([
    #image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ],
            className="p-1 px-0 py-0"),
    dbc.Row(html.Div([html.Hr(className="my-2"),
                      html.H1("")],
                     ),
            className="h-10"),

    # Disclaimer
    dbc.Row(
        dbc.Col(html.Div([
            html.H6(dcc.Markdown('''**DISCMLAIMER**: This is not financial advice, this is just a data project. 
            What you do with that data is up to you. Any predictions are simply machine learning results based on 
            the underlying data, and not actual financial recommendations.
            '''))
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(html.Div([html.Hr(className="my-2"),
                      html.H1("")],
                     ),
            className="h-10"),

    #     #
    # FAQ #
    #     #
    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''FAQ''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),

    # Thesis
    dbc.Row(dbc.Col(html.Div(
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        dcc.Markdown('''**Causalation** Is a project to designed to make it easier to use information
                    from SEC filings in quantitative analysis.'''),

                        dcc.Markdown('''There is so much data available today, and retail traders want 
                    to use that data to inform their stock picks. However, data analysis is hard, and the only 
                    options available today are: 
                    '''),
                        dcc.Markdown('''
                        **1.** Download raw (and expensive) datasets, then do a ton of coding to make it actionable

                        **2.** Pay someone for their own picks that lack transparency around the process and the 
                        success of the models

                        **My primary goal** is to find somewhere inbetween where I can surface interesting and actionable
                        data for everyone. I started with SEC data because that seems the most interesting for 
                        momentum based strategies, but I will consider adding other data sources in the future.

                        **As a secondary goal**, I want to take this data one step further and use it myself to build an 
                        effective quantitative strategy.

                        The blog will follow the results of that secondary focus and use that information to improve
                        this website.

                        '''),
                    ],
                    title="What is Causalation?", )],
            start_collapsed=True,
        ), ),
        style={'textAlign': 'left'},
        width={"size": 8, "offset": 2},
    )
    ),

    #Dashboard Details
    dbc.Row(
        dbc.Col(html.Div([
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            html.Img(src=images.screenshot_helper,
                                     style={'height': '5%', 'width': '80%'}),
                            dcc.Markdown(
                                '''
            **1:** Filter by Stock
            
            **2:** Filter by Date. 10-K's have data going back to January 2017; 10-Q's to January 2021.
            
            **3:** Filter by number of week delay. This allows you to correlate stocks with topics mentioned X number 
            of weeks ago
            
            **4:** Filter by Filing Type. 10-K's, 10-Q's, or both
            
            **5:** Filter by keywords mentioned. Each keyword includes all larger words. e.g. "cloud computing" would 
            be captured by "cloud"
            
            **6:** Apply filters to the entire page
            
            **7:** This chart shows each stock's closing price for a given week and the percentage of SEC Filings that 
            mention the keyword selected. The keyword selected is cohorted by week and the percentage represented in the chart 
            is based on a 12 week rolling average
            
            **8:** The returns of the stock in the given timeframe
            
            **9:** The returns of the S&P 500 during the same timeframe to make benchmarking easier
            
            **10:** The number of times the stock follows the moves of the keyword mentions with the filters applied. Example:
            you have the delay filter set to 2 weeks and the keyword mentions increase in a one week timeframe. Then two 
            weeks later, the stock price increases as well. That would count as a match. If the moves match 50 out of 
            100 times, this value will show 50%.
            
            **11:** Total number of times this keyword is mentioned within the timeframe selected
            
            **12:** The correlation ratio between the stock and the keyword selected, within the given filters
            
            **13:** This table is not affected by the filters, but instead updates everyday to show the 10 sets of 
            filters with the strongest correlation
                                '''), ],
                        title="What's on the Historical Dashboard?", )],
                start_collapsed=True, )
        ]),
            style={'textAlign': 'left', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),

    # ML Strategy
    dbc.Row(
        dbc.Col(html.Div([
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Markdown(
                                '''**Current Model Strategy:** SEC Filings contain language in the sections about risk 
                                that are meant to be boiler plate and broad. However, when you assess the trends over time 
                                of companies deciding these warnings are/aren't necessary, you can accurately predict the 
                                directional movement of stocks that are strongly correlated to broad market shifts.'''), ],
                        title="What's the Strategy for the ML Predictions?", )],
                start_collapsed=True, )
        ]),
            style={'textAlign': 'left', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),

    #Data Details
    dbc.Row(
        dbc.Col(html.Div([
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Markdown(
                                '''
                                The stock data is the current S&P 500, plus some meme stocks that people have asked
                                for. The SEC filings are only from the S&P 500 companies. 
                                
                                By using the current list of S&P 500 companies, that will create some survivorship bias.
                                Maybe in the future we will use point in time data.
                                '''), ],
                        title="What Data is Being Used?", )],
                start_collapsed=True, )
        ]),
            style={'textAlign': 'left', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Markdown(
                                '''The data is pulled from SEC public filings. Text is then extracted from the sections 
                4 "Risk Factors" and 7 "Management’s Discussion and Analysis of Financial Condition and Results of 
                Operations"'''), ],
                        title="How is the SEC Filing Data Normalized?", )],
                start_collapsed=True, )
        ]),
            style={'textAlign': 'left', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [
                            dcc.Markdown(
                                '''
                                The chart includes the 12 week rolling average of keyword mentions- this ensures that 
                                a slow week in filings doesn't distort the data. But to ensure that the first few weeks 
                                also aren't dramatic swings, the first 6 datapoints are disregarded. 
                                
                                This is true both for the chart on the historical dashboard, and for the data used to 
                                build the ML Models'''), ],
                        title="Why isn't the Start Date on the Chart What I Selected?", )],
                start_collapsed=True, )
        ]),
            style={'textAlign': 'left', 'color': colors['text']},
            width={"size": 8, "offset": 2},
        ),
        className="p-5 px-0 py-0 pb-5"
    ),
])

