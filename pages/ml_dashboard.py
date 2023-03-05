import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import dataframes_from_queries
import pandas as pd
import dash_components.charts as my_dash_charts
import sidebar as sidebar
from cron_jobs import get_dates
import ml_models.backtest as backtest

import images as my_images
import base64

dash.register_page(__name__, path='/predictions', name="Predictions")

colors = {
    'background': '#D3D3D3',
    'text': '#00008B'
}

layout = dbc.Container([
    html.Div(html.H2(
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
        dbc.Col(html.Div(id="stocks_to_buy_table"), width={"size": 8, "offset": 2})
    ),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart_backtest', figure={})), width={"size": 9, "offset": 2})),
    html.Div(html.H1(
        children='Top Stock Correlations',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        dbc.Col(html.Div(id="ml_list_of_top_accuracy_table"), width={"size": 8, "offset": 2})
    ),
    # dbc.Row(dbc.Col(html.Div(html.P(
    #     id="ml_top_five_accuracy_list",
    #     style={
    #         'textAlign': 'center',
    #         'color': colors['text']
    #     })),
    #     width={"size": 12, "offset": 1})),
    dbc.Row(
        dbc.Col(html.Div(id="ml_top_five_accuracy_table"), width={"size": 10, "offset": 1})
    ),
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
                html.Div(dbc.Button("Apply Filters", id='my_button_2', color="primary", className="me-1", n_clicks=0)
                         ),
                width={"size": 2})
        ],
        className="g-2"
    ),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart_2', figure={})), width={"size": 9, "offset": 2})),
])


@callback(
    Output('date_and_stock_for_chart_2', 'figure'),
    Output('date_and_stock_for_chart_backtest', 'figure'),
    Output('ml_top_five_accuracy_table', 'children'),
    Output('ml_list_of_top_accuracy_table', 'children'),
    Output('stocks_to_buy_table', 'children'),
    Input('my_button_2', 'n_clicks'),
    [State('dropdown_input_2', 'value'),
     State('filing_type_dropdown_input_2', 'value'),
     State('week_delay_dropdown_input_2', 'value'),
     State('keyword_dropdown_input_2', 'value'),
     State('date_picker_range_2', 'start_date'),
     State('date_picker_range_2', 'end_date')
     ]
)
def ml_update_output(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                  keyword_dropdown_value, start_date, end_date):
    if len(stock_dropdown_value) > 0:
        print(n_clicks)
        date_and_stock_for_chart_2 = my_dash_charts.Edgar_Mult_Y_Axis_Lines(
            dataframes_from_queries.inflation_mention_chart(stock_dropdown_value, start_date,
                                                            end_date, keyword_dropdown_value, '', filing_type_value),
            stock_dropdown_value, keyword_dropdown_value)
        date_and_stock_for_chart_backtest = my_dash_charts.backtest_Mult_Y_Axis_Lines(
            backtest.comparing_returns_vs_sandp())
        ml_data_for_table = dataframes_from_queries.calculate_ml_model_accuracy()
        ml_top_five_accuracy_table = my_dash_charts.generate_table_with_filters(ml_data_for_table[0])
        ml_list_of_top_accuracy_table = my_dash_charts.generate_table(ml_data_for_table[2])
        stocks_to_buy_table = my_dash_charts.generate_table(dataframes_from_queries.stocks_to_buy_this_week())
        # buy_date_text = dataframes_from_queries.buy_date()
        print("filter_applied")
    elif len(stock_dropdown_value) == 0:
        raise exceptions.PreventUpdate
    return date_and_stock_for_chart_2, date_and_stock_for_chart_backtest, \
           ml_top_five_accuracy_table, ml_list_of_top_accuracy_table, stocks_to_buy_table