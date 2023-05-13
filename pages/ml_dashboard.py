import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import dataframes_from_queries
import dash_components.charts as my_dash_charts
from cron_jobs import get_dates
import precise_backtest as backtest
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/predictions', name="Predictions")


layout = dbc.Container([
    # image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'height': '2%', 'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ]),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

    #Recommendation Section
    html.Div(html.H1(
        children='Stock Predictions This Week',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),

    # webfom
    dbc.Row(dbc.Col([
        html.Div(html.H6(dcc.Markdown('''Predictions are refreshed every Sunday morning for the next Monday. Never miss 
        the latest prediction by signing up for our newsletter!'''),
                         style={
                             'textAlign': 'center',
                             'fontWeight': '400',
                             'color': colors['text']
                         })),
    html.Form(
        action="https://buttondown.email/api/emails/embed-subscribe/Causalation?tag=website",
        method="post",
        target="popupwindow",
        className="embeddable-buttondown-form",
        children=[
            dcc.Input(type="email", name="email", placeholder="you@example.com"),
            dcc.Input(type="hidden", value="1", name="embed"),
            dcc.Input(type="submit", value="Subscribe"),
            html.P(
                html.A("Powered by Buttondown.", href="https://buttondown.email/Causalation", target="_blank")
            ),
        ],
        style={
            'textAlign': 'center',
            'color': colors['text']
        })], width={"size": 10, "offset": 1})
    ),
    dbc.Row(
        dbc.Col(html.Div(id="stocks_to_buy_table"), width={"size": 10, "offset": 1})
    ),
    dbc.Row(dbc.Col(html.Div(html.H6(dcc.Markdown('''Want to see detailed commentary on the accuracy of previous weeks?
                [Check out our blog](/blog)!'''),
                                 style={
                                     'textAlign': 'center',
                                     'fontWeight': '600',
                                 })),
                    width={"size": 10, "offset": 1})
    ),

    #last week. Need to fix the query before this can be put back in
    # html.Div(html.Hr(className="my-2")),
    # dbc.Row(
    #     dbc.Col([html.Div(html.H1(
    #                 children='Stocks Recommendations Last Week',
    #                 style={
    #                     'textAlign': 'center',
    #                     'color': colors['text']
    #                 })),
    #         html.Div(html.H6(dcc.Markdown('''Want to see detailed commentary on the accuracy of previous weeks?
    #         [Check out our blog](/blog)!'''),
    #                          style={
    #                              'textAlign': 'center',
    #
    #                          })),
    #             html.Div(html.H3(
    #                 children='Last Week Returns:',
    #                 style={
    #                     'textAlign': 'center',
    #                     'color': colors['text']
    #                 })),
    #                 html.Div(html.H3(id='last_week_returns'),
    #                          style={
    #                              'textAlign': 'center',
    #                              'color': colors['text']
    #                          }),
    #             html.Div(id="stocks_to_buy_last_week_table")],
    #             width={"size": 10, "offset": 1})
    # ),

    #Backtesting Section
    html.Div(html.Hr(className="my-2")),
    html.Div(html.H1(
        children='Backtest Results Compared to S&P 500',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(html.Div([html.P()])),
    dbc.Row(
        [dbc.Col(html.Div(html.H3("S&P 500 Returns:"),
                          style={
                              'textAlign': 'center',
                              'color': colors['text']
                          }), width={"size": 3, "offset": 2}),
         dbc.Col(html.Div(html.H3("Backtest Returns:"),
                          style={
                              'textAlign': 'center',
                              'color': colors['text']
                          }), width={"size": 3, "offset": 2})
         ]
    ),
    dbc.Row(
        [dbc.Col(html.Div(html.H3(id='s_and_p_returns'),
        style={
            'textAlign': 'right',
            'color': colors['text']
        }), width={"size": 3, "offset": 1}),
         dbc.Col(html.Div(html.H3(id='backtest_returns'),
        style={
            'textAlign': 'right',
            'color': colors['text']
        }), width={"size": 3, "offset": 2})
        ]
    ),
    dbc.Row(
         dbc.Col(html.Div([html.H3("Sharpe Ratio:"),
                           html.H3(id='sharpe_ratio')],
                          style={
                              'textAlign': 'center',
                              'color': colors['text']
                          }), width={"size": 4, "offset": 4})
    ),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart_backtest', figure={})),
                    width={"size": 9, "offset": 2})),


    #Prediction Table unfurl section
    dbc.Row(html.Div([html.P()])),
    dbc.Row(
        dbc.Button("See Weekly Prediction Accuracy", id="collapse-button", className='d-grid gap-2', n_clicks=0,
                   style={"background-color": colors['mid_theme']})),
    dbc.Row(html.Div([html.P()])),
    dbc.Collapse(
        dbc.Row(dbc.Col(html.Div(id="ml_top_five_accuracy_table"), width={"size": 10})),
        id='collapse_table',
        is_open=False,
    ),
    dbc.Row(html.Div([html.P()])),

    #Correlation collapsed section
    dcc.Interval(
        id="load_interval",
        n_intervals=0,
        max_intervals=0,
        interval=1
    ),

    ])


@callback(
    Output('date_and_stock_for_chart_backtest', 'figure'),
    # Output('decision_tree_chart_backtest', 'figure'),
    # Output('linear_chart_backtest', 'figure'),
    Output('ml_top_five_accuracy_table', 'children'),
    Output('stocks_to_buy_table', 'children'),
    Output('s_and_p_returns', 'children'),
    Output('backtest_returns', 'children'),
    # Output('stocks_to_buy_last_week_table', 'children'),
    # Output('last_week_returns', 'children'),
    Output('sharpe_ratio', 'children'),
    Input('load_interval', 'n_intervals'),
    prevent_initial_call=False
)
def ml_update_output(n_intervals):
    date_and_stock_for_chart_backtest = my_dash_charts.backtest_Mult_Y_Axis_Lines(
        backtest.comparing_returns_vs_sandp('decision_tree')[0])
    s_and_p_returns = backtest.comparing_returns_vs_sandp('decision_tree')[1]
    backtest_returns = backtest.comparing_returns_vs_sandp('decision_tree')[2]
    sharpe_ratio = backtest.comparing_returns_vs_sandp('decision_tree')[3]
    backtest_all_results_df = backtest.backtesting_buy_recommendation_list('decision_tree')
    ml_top_five_accuracy_table = my_dash_charts.generate_table_with_filters(backtest_all_results_df[2])
    stocks_to_buy_table = my_dash_charts.generate_table(
        dataframes_from_queries.stocks_to_buy_this_week(1000, 'future_buy_recommendations')[0])
    # stocks_to_buy_last_week_table = my_dash_charts.generate_table(
    #     dataframes_from_queries.stocks_to_buy_this_week(1000, 'last_week_buy_recommendations')[0])
    # last_week_returns = dataframes_from_queries.stocks_to_buy_this_week(1000, 'last_week_buy_recommendations')[1]
    # buy_date_text = dataframes_from_queries.buy_date()
    return date_and_stock_for_chart_backtest, ml_top_five_accuracy_table, \
           stocks_to_buy_table, s_and_p_returns, backtest_returns, sharpe_ratio
           # decision_tree_chart_backtest, linear_chart_backtest, \


#collapse for the table of raw accuracy information
@callback(
Output('collapse_table', 'is_open'),
[Input('collapse-button', 'n_clicks')],
State('collapse_table', 'is_open')
)
def toggle_collapse_table(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

