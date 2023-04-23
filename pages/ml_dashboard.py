import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import dataframes_from_queries
import time
import pandas as pd
import dash_components.charts as my_dash_charts
import sidebar as sidebar
from cron_jobs import get_dates
# import ml_models.backtest as backtest
import precise_backtest as backtest
from static.color_palette import colors

import images as my_images
import base64

dash.register_page(__name__, path='/predictions', name="Predictions")


layout = dbc.Container([
    #Recommendation Section
    html.Div(html.H1(
        children='Stocks to Buy This Week',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        dbc.Col(
            html.Div(html.H6(dcc.Markdown('''Want to see previous recommendations, as well as commentary on the accuracy? 
    [Check out our blog](/blog)!
    '''),
        style={
            'textAlign': 'center',

        })),
        width={"size": 10, "offset": 1}
        )),
    dbc.Row(
        dbc.Col(html.Div(id="stocks_to_buy_table"), width={"size": 10, "offset": 1})
    ),
    dbc.Row(
        dbc.Col([html.Div(html.H1(
                    children='Stocks Recommendations Last Week',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    })),
                html.Div(html.H3(
                    children='Last Week Returns:',
                    style={
                        'textAlign': 'center',
                        'color': colors['text']
                    })),
                    html.Div(html.H3(id='last_week_returns'),
                             style={
                                 'textAlign': 'center',
                                 'color': colors['text']
                             }),
                html.Div(id="stocks_to_buy_last_week_table")],
                width={"size": 10, "offset": 1})
    ),
    html.Div(html.H1(
        children='Top Stock Correlations Today',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        dbc.Col(html.Div(id="ml_list_of_top_accuracy_table"), width={"size": 8, "offset": 2})
    ),

    #Backtesting Section
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
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart_backtest', figure={})),
                    width={"size": 9, "offset": 2})),
    # html.Div(html.H3(
    #     children='Decision Tree Model',
    #     style={
    #         'textAlign': 'center',
    #         'color': colors['text']
    #     })),
    # dbc.Row(dbc.Col(html.Div(dcc.Graph(id='decision_tree_chart_backtest', figure={})), width={"size": 9, "offset": 2})),
    # html.Div(html.H3(
    #     children='Linear Regression Model',
    #     style={
    #         'textAlign': 'center',
    #         'color': colors['text']
    #     })),
    # dbc.Row(dbc.Col(html.Div(dcc.Graph(id='linear_chart_backtest', figure={})), width={"size": 9, "offset": 2})),
    # dbc.Row(dbc.Col(html.Div(html.P(
    #     id="ml_top_five_accuracy_list",
    #     style={
    #         'textAlign': 'center',
    #         'color': colors['text']
    #     })),
    #     width={"size": 12, "offset": 1})),

    #Prediction Table unfurl section
    dbc.Row(html.Div([html.P()])),
    dbc.Row(
        dbc.Button("See Weekly Prediction Accuracy", id="collapse-button", className='d-grid gap-2', color="primary",
                   n_clicks=0)),
    dbc.Row(html.Div([html.P()])),
    dbc.Collapse(
        dbc.Row(dbc.Col(html.Div(id="ml_top_five_accuracy_table"), width={"size": 10})),
        id='collapse_table',
        is_open=False,
    ),
    dbc.Row(html.Div([html.P()])),
    dbc.Row(
        dbc.Button("See Correlation Chart", id="collapse-button-explore-data", className='d-grid gap-2', color="primary",
                   n_clicks=0)),
    dbc.Row(html.Div([html.P()])),
    # dbc.Row(
    #     dbc.Col(html.Div(id="ml_top_five_accuracy_table"), width={"size": 10, "offset": 1})
    # ),

    #Correlation collapsed section
    dbc.Collapse(
        dbc.Row(
            [
                dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_dropdown(),
                                               id='dropdown_input_2', placeholder='GME', value='GME')
                                  ],
                                 ), width={"size": 1, "offset": 2}),
                dbc.Col(html.Div([dcc.DatePickerRange(id='date_picker_range_2',
                                                      start_date=date(2017, 1, 1),
                                                      end_date=get_dates(),
                                                      clearable=False)], ),
                        width={"size": 3}),
                dbc.Col(html.Div([dcc.Dropdown(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
                                                '15', '16', '17', '18', '19', '20'],
                                               id='week_delay_dropdown_input_2', value='4')
                                  ],
                                 ), width={"size": 1}),
                dbc.Col(html.Div([dcc.Dropdown(options=[
                    {'label': '10-K', 'value': '10-Q'},
                    {'label': '10-Q', 'value': '10-K'},
                    {'label': 'Both', 'value': ''}],
                    id='filing_type_dropdown_input_2', value='10-K')
                ],
                ), width={"size": 1}),
                dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.keyword_list,
                                               id='keyword_dropdown_input_2', value='cloud')
                                  ],
                                 ), width={"size": 2}),
                dbc.Col(
                    html.Div(dbc.Spinner(
                        dbc.Button("Apply Filters", id='my_button_2', color="primary", className="me-1", n_clicks=0,
                                        disabled=True,
                                        loading_state={'is_loading': True})
                             )),
                    width={"size": 2}
                )
            ],
            className="g-2"
        ),
        id='collapse_filters',
        is_open=False,
    ),
    dbc.Collapse(
        dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart_2', figure={})), width={"size": 9, "offset": 2})),
        id='collapse_edgar_chart',
        is_open=False,),
    dbc.Row(html.Div([dcc.Markdown('''
    
    
    ''')])),
    ])


@callback(
    Output('date_and_stock_for_chart_2', 'figure'),
    Output('date_and_stock_for_chart_backtest', 'figure'),
    # Output('decision_tree_chart_backtest', 'figure'),
    # Output('linear_chart_backtest', 'figure'),
    Output('ml_top_five_accuracy_table', 'children'),
    Output('ml_list_of_top_accuracy_table', 'children'),
    Output('stocks_to_buy_table', 'children'),
    Output('s_and_p_returns', 'children'),
    Output('backtest_returns', 'children'),
    Output('stocks_to_buy_last_week_table', 'children'),
    Output('last_week_returns', 'children'),
    Input('my_button_2', 'n_clicks'),
    [State('dropdown_input_2', 'value'),
     State('filing_type_dropdown_input_2', 'value'),
     State('week_delay_dropdown_input_2', 'value'),
     State('keyword_dropdown_input_2', 'value'),
     State('date_picker_range_2', 'start_date'),
     State('date_picker_range_2', 'end_date'),
     ],
    prevent_initial_call=False
)
def ml_update_output(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                  keyword_dropdown_value, start_date, end_date):
    if len(stock_dropdown_value) > 0:
        print(n_clicks)
        date_and_stock_for_chart_2 = my_dash_charts.Edgar_Mult_Y_Axis_Lines(
            dataframes_from_queries.inflation_mention_chart(stock_dropdown_value, start_date,
                                                            end_date, keyword_dropdown_value, '', filing_type_value)[0],
            stock_dropdown_value, keyword_dropdown_value)
        date_and_stock_for_chart_backtest = my_dash_charts.backtest_Mult_Y_Axis_Lines(
            backtest.comparing_returns_vs_sandp('random_forest')[0])
        s_and_p_returns = backtest.comparing_returns_vs_sandp('random_forest')[1]
        backtest_returns = backtest.comparing_returns_vs_sandp('random_forest')[2]
        # decision_tree_chart_backtest = my_dash_charts.backtest_Mult_Y_Axis_Lines(
        #     backtest.comparing_returns_vs_sandp('decision_tree'))
        # linear_chart_backtest = my_dash_charts.backtest_Mult_Y_Axis_Lines(
        #     backtest.comparing_returns_vs_sandp('linear'))
        ml_data_for_table = dataframes_from_queries.calculate_ml_model_accuracy()
        backtest_all_results_df = backtest.backtesting_buy_recommendation_list('random_forest')
        ml_top_five_accuracy_table = my_dash_charts.generate_table_with_filters(backtest_all_results_df[2])
        # ml_top_five_accuracy_table = my_dash_charts.generate_table_with_filters(ml_data_for_table[0])
        ml_list_of_top_accuracy_table = my_dash_charts.generate_table(ml_data_for_table[2])
        stocks_to_buy_table = my_dash_charts.generate_table(
            dataframes_from_queries.stocks_to_buy_this_week(1000, 'future_buy_recommendations')[0])
        stocks_to_buy_last_week_table = my_dash_charts.generate_table(
            dataframes_from_queries.stocks_to_buy_this_week(1000, 'last_week_buy_recommendations')[0])
        last_week_returns = dataframes_from_queries.stocks_to_buy_this_week(1000, 'last_week_buy_recommendations')[1]
        # buy_date_text = dataframes_from_queries.buy_date()
        print("filter_applied")
    elif len(stock_dropdown_value) == 0:
        raise exceptions.PreventUpdate
    return date_and_stock_for_chart_2, date_and_stock_for_chart_backtest, ml_top_five_accuracy_table, \
           ml_list_of_top_accuracy_table, stocks_to_buy_table, s_and_p_returns, backtest_returns, \
           stocks_to_buy_last_week_table, last_week_returns
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


@callback(
Output('collapse_filters', 'is_open'),
[Input('collapse-button-explore-data', 'n_clicks')],
State('collapse_filters', 'is_open')
)
def toggle_collapse_filters(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open


@callback(
Output('collapse_edgar_chart', 'is_open'),
[Input('collapse-button-explore-data', 'n_clicks')],
State('collapse_edgar_chart', 'is_open')
)
def toggle_collapse_edgar_chart(n_clicks, is_open):
    if n_clicks:
        return not is_open
    return is_open

@callback(
    Output('my_button_2', 'disabled'),
    Input('my_button_2', 'n_clicks')
)
def disable_button(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        disabled = True
    else:
        disabled = False
    return disabled

@callback(
    Output('my_button_2', 'n_clicks'),
    Input('my_button_2', 'n_clicks'),
    State('dropdown_input_2', 'value'),
    State('filing_type_dropdown_input_2', 'value'),
    State('week_delay_dropdown_input_2', 'value'),
    State('keyword_dropdown_input_2', 'value'),
    State('date_picker_range_2', 'start_date'),
    State('date_picker_range_2', 'end_date')
)
def reset_n_clicks(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                   keyword_dropdown_value, start_date, end_date):
    if n_clicks is not None and n_clicks > 0:
        # Call the function that applies the filters
        ml_update_output(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                         keyword_dropdown_value, start_date, end_date)
        return 0
    else:
        return n_clicks

