import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import dataframes_from_queries
import dash_components.charts as my_dash_charts
from cron_jobs import get_dates
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/dashboard', name="Dashboard")

# colors = {
#     'background': '#FFFFFF',
#     'text': '#000000'
# }


layout = html.Div(children=[dbc.Container([
    # image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'height': '2%', 'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ]),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

    #Filters
    dbc.Row(html.Div(html.H4(""))),
    dbc.Row(
        [
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_dropdown(),
                                           id='dropdown_input', placeholder='GME', value='GME')
                              ],
                             ), width={"size": 1, "offset": 2}),
            dbc.Col(html.Div([dcc.DatePickerRange(id='date_picker_range',
                                                  start_date=date(2017, 1, 1),
                                                  end_date=get_dates(),
                                                  clearable=False)], ),
                    width={"size": 3}),
            dbc.Col(html.Div([dcc.Dropdown(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14',
                                            '15', '16', '17', '18', '19', '20'],
                                           id='week_delay_dropdown_input', value='4')
                              ],
                             ), width={"size": 1}),
            dbc.Col(html.Div([dcc.Dropdown(options=[
                {'label': '10-K', 'value': '10-Q'},
                {'label': '10-Q', 'value': '10-K'},
                {'label': 'Both', 'value': ''}],
                                           id='filing_type_dropdown_input', value='10-K')
                              ],
                             ), width={"size": 1}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.keyword_list,
                                           id='keyword_dropdown_input', value='cloud')
                              ],
                             ), width={"size": 2}),
            dbc.Col(
                html.Div(
                    dbc.Spinner(
                    dbc.Button("Apply Filters", id='my_button', color="primary", className="me-1", n_clicks=0,
                               disabled=True,
                               loading_state={'is_loading': True})
                )),
                width={"size": 2}
            )
        ],
        className="g-2"
    ),

    #table
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart', figure={})), width={"size": 9, "offset": 2})),
    dbc.Row(html.Div(html.Hr(className="my-2"))),

    # stock returns
    html.Div(html.H1(
        children='Stock Data',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    ),
    dbc.Row([dbc.Col(html.Div([html.H3("Stock Returns:"),
                               html.H3(id='stock_returns')],
                              style={
                                  'textAlign': 'center',
                                  'color': colors['text']
                              }), width={"size": 3, "offset": 2}),
             dbc.Col(html.Div([html.H3("S&P 500 Returns:"),
                               html.H3(id='s_and_p_returns_for_daterange')],
                              style={
                                  'textAlign': 'center',
                                  'color': colors['text']
                              }), width={"size": 3, "offset": 2}),
             ]
            ),
    dbc.Row(dbc.Col(html.Div([html.H3("Stock Follows SEC Direction:"),
                          html.H3(id='stock_and_sec_move_table'),
                              html.H3("")],
                         style={
                             'textAlign': 'center',
                             'color': colors['text']
                         }), width={"size": 4, "offset": 4})),
    dbc.Row(html.Div(html.Hr(className="my-2"))),

    #Counts

    html.Div(html.H1(
        children='Keyword Data',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    ),
    dbc.Row([
        # dbc.Col(html.Div(id="correlation_table"), width={"size": 3, "offset": 2}),
        dbc.Col(html.Div(id="keyword_count_table"), width={"size": 4, "offset": 1}),
        dbc.Col(html.Div(id="keyword_correlation_table"), width={"size": 4, "offset": 1}),
    ]),

    #top correlation section
    html.Div(html.Hr(className="my-2")),
    html.Div(html.H1(
        children='Top Stock Correlations Today',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        dbc.Col(html.Div(id="ml_list_of_top_accuracy_table"), width={"size": 8, "offset": 2})
    ),


    #Junkyard
    # dbc.Row(html.Div(html.Hr(className="my-2"))),
    # html.Div(html.H1(
    #     children='Top Stocks Correlated',
    #     style={
    #         'textAlign': 'center',
    #         'color': colors['text']
    #     }),
    # ),
    # dbc.Row(dbc.Col(html.Div([html.P('''With the Filters Applied''')]),
    #                 style={'textAlign': 'center'},
    #                 width={"size": 8, "offset": 2},
    #                 )
    #         ),
    # dbc.Row(
    #     [
    #         dbc.Col(html.Div(id="desc_correlation_table"), width={"size": 3, "offset": 2}),
    #         dbc.Col(html.Div(id="asc_correlation_table"), width={"size": 3, "offset": 1})
    #     ]
    # ),
    # html.Div(style={'display': 'none'}, children=[
    #     dcc.Input(id='trigger_on_pageload', value=0, style={'display': 'none'})
    # ])
      # html.Div(html.H1(
      #     children='Data from Chart Above',
      #     style={
      #         'textAlign': 'center',
      #         'color': colors['text']
      #     })),
      # dbc.Row(
      #         dbc.Col(html.Div(id="data_from_chart"), width={"size": 6, "offset": 3})
      # )
        ])
                  ])



@callback(
    Output('date_and_stock_for_chart', 'figure'),
    Output('keyword_correlation_table', 'children'),
    Output('keyword_count_table', 'children'),
    Output('stock_returns', 'children'),
    Output('s_and_p_returns_for_daterange', 'children'),
    Output('stock_and_sec_move_table', 'children'),
    Output('ml_list_of_top_accuracy_table', 'children'),
    # Output('correlation_table', 'children'),
    # Output('desc_correlation_table', 'children'),
    # Output('asc_correlation_table', 'children'),
    # Output('date_picker_range', 'end_date'),
    # Output('data_from_chart', 'children'),
    Input('my_button', 'n_clicks'),
    [State('dropdown_input', 'value'),
     State('filing_type_dropdown_input', 'value'),
     State('week_delay_dropdown_input', 'value'),
     State('keyword_dropdown_input', 'value'),
     State('date_picker_range', 'start_date'),
     State('date_picker_range', 'end_date')
     ]
)
def update_output(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                  keyword_dropdown_value, start_date, end_date):
    if len(stock_dropdown_value) > 0:
        print(n_clicks)
        edgar_chart_data, stock_return_data = dataframes_from_queries.inflation_mention_chart(stock_dropdown_value, start_date,
                                                            end_date, keyword_dropdown_value, '', filing_type_value)
        edgar_chart = my_dash_charts.Edgar_Mult_Y_Axis_Lines(edgar_chart_data, stock_dropdown_value, keyword_dropdown_value)
        keyword_correlation_table = my_dash_charts.generate_table(
            dataframes_from_queries.inflation_mention_correlation(stock_dropdown_value, start_date, end_date,
                                                    keyword_dropdown_value, week_delay_dropdown_value, filing_type_value))
        keyword_count_table = my_dash_charts.generate_table(
            dataframes_from_queries.keyword_table(keyword_dropdown_value, start_date, end_date))

        s_and_p_returns = dataframes_from_queries.s_and_p_returns_for_daterange(start_date, end_date)
        stock_and_sec_move_table = dataframes_from_queries.stock_moving_with_sec_data(stock_dropdown_value, start_date,
                                        end_date, keyword_dropdown_value, week_delay_dropdown_value, filing_type_value)
        ml_list_of_top_accuracy_table = my_dash_charts.generate_table(dataframes_from_queries.daily_top_ten_correlations())
        # dropdown_table = my_dash_charts.generate_table(
        #     dataframes_from_queries.stock_crypto_correlation_filtered(stock_dropdown_value))
        # descending_correlation_table = my_dash_charts.generate_table(
        #         dataframes_from_queries.top_keyword_correlations_with_rolling_avg('desc', keyword_dropdown_value,
        #                                             start_date, end_date, week_delay_dropdown_value, filing_type_value)),
        # ascending_correlation_table = my_dash_charts.generate_table(
        #         dataframes_from_queries.top_keyword_correlations_with_rolling_avg('asc', keyword_dropdown_value,
        #                                             start_date, end_date, week_delay_dropdown_value, filing_type_value))
        # data_from_chart = my_dash_charts.generate_table(
        #     dataframes_from_queries.inflation_mention_chart(stock_dropdown_value, start_date,
        #                                             end_date, keyword_dropdown_value, 'limit 30', filing_type_value))
        print("filter_applied")
    elif len(stock_dropdown_value) == 0:
        raise exceptions.PreventUpdate
    return edgar_chart, keyword_correlation_table, keyword_count_table, stock_return_data, s_and_p_returns, \
           stock_and_sec_move_table, ml_list_of_top_accuracy_table
        # , data_from_chart

@callback(
    Output('my_button', 'disabled'),
    Input('my_button', 'n_clicks')
)
def disable_button(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        disabled = True
    else:
        disabled = False
    return disabled

@callback(
    Output('my_button', 'n_clicks'),
    Input('my_button', 'n_clicks'),
    State('dropdown_input', 'value'),
    State('filing_type_dropdown_input', 'value'),
    State('week_delay_dropdown_input', 'value'),
    State('keyword_dropdown_input', 'value'),
    State('date_picker_range', 'start_date'),
    State('date_picker_range', 'end_date')
)
def reset_n_clicks(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                   keyword_dropdown_value, start_date, end_date):
    if n_clicks is not None and n_clicks > 0:
        # Call the function that applies the filters
        update_output(n_clicks, stock_dropdown_value, filing_type_value, week_delay_dropdown_value,
                         keyword_dropdown_value, start_date, end_date)
        return 0
    else:
        return n_clicks