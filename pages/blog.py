import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/blog')


layout = dbc.Container([
    # image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'height': '2%', 'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ]),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

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
        dcc.Markdown('''**My Thesis:** There is so much data available today, and more retail traders want to use that 
        data to inform their stock picks. However, data analysis is hard, and the only options available today are: 
        
        1. Download raw (and expensive) datasets, then do a ton of coding to make it actionable
        2. Pay someone for their own picks that lack transparency around the process and the success of the models
        
        Instead, I think there is value in exposing my own process to quant trading so that you can use my learnings to 
        inform your own process. My main focus will be to share clean and actionable data that underpins my own
        quant strategies. My secondary focus is to publish the results of my quant strategy so that you can follow along. 
        If the strategy is successful, then it will be something I can bill for. 
         
        This blog will follow the results of that secondary focus.
        
        **My Current Trading Strategy:** SEC Filings contain language in the sections about risk that are meant to be 
        boiler plate and broad. However, when you assess the trends over time of companies deciding these 
        warnings are/aren't necessary, you can accurately predict the directional movement of stocks that are 
        strongly correlated to broad market shifts.
        
        '''),
        # html.P('''My Thesis: By pulling together public data sources and making them searchable,
        # I can make market data more accessible to everyday traders. And if I use this data effectively,
        # I can develop trading strategies for myself.'''),
        # html.P(
        #         '''My Current Hypothesis: SEC Filings contain language in the sections about risk that are meant to be
        #         boiler plate and broad. However, when you assess the trends over time of companies deciding these
        #         warnings are/aren't necessary, you can accurately predict the directional movement of stocks that are
        #         strongly correlated to broad market shifts.'''),
        #     html.P(
        #         '''Follow along in these blog posts to see how the model changes over time and whether or not
        #         the recommendations are profitable'''),
        ]),
            style={'textAlign': 'center'},
            width={"size": 8, "offset": 2},
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 3/12/2023"),
                                      href="/blog_pages/3_12_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 3/5/2023"),
                                      href="/blog_pages/3_5_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 2/18/2023"),
                                      href="/blog_pages/2_18_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 2/13/2023"),
                                      href="/blog_pages/2_12_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
])

