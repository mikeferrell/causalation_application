import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import time
from ml_models import dataframes_from_queries
import dash_components.charts as my_dash_charts
from cron_jobs import get_dates
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/price_drops', name="Price Drops")


layout = dbc.Container([
    # image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'height': '2%', 'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ]),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

    #Title
    html.Div(html.H1(
        children='Is the Stock On Sale?',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    html.Div(html.H6(dcc.Markdown('''Compare current company financials with financials when the stock price was at 
                                  its peak'''),
             style={
                 'textAlign': 'center',
                 'fontWeight': '400',
                 'color': colors['text']
             })),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

    #Numeric Filters
    dbc.Row([html.H4("Related Filters"),
        html.P(id="filter_error_message",
                   style={
                       'textAlign': 'left',
                       'color': colors['red_button']
                   })]),
    dbc.Row([
            dbc.Col(html.Div([dcc.Dropdown(['Company Name', 'Stock Symbol', 'Price Change', 'Highest Price', 'Current Price',
                        'Days Since Peak Price', 'Peak Price Date', 'Cash Growth Since Peak', 'Asset Growth Since Peak',
                        'Company Value Change', 'Peak Company Value', 'Most Recent Company Value', 'EPS Change',
                        'EPS at Peak Price', 'Most Recent EPS',
                        'Price to Sales Ratio Change', 'Peak Price to Sales Ratio', 'Most Recent Price to Sales Ratio',
                        'P/E Ratio Change', 'Peak P/E Ratio', 'Most Recent P/E Ratio',
                        'EBITDA Change', 'Peak Price EBITDA', 'Most Recent EBITDA'],
                                           id='order_by', placeholder='Filter by Column', value='')
                              ],
                             ), width={"size": 3}),
            dbc.Col(html.Div(
                [
                    dbc.Input(type="number", size="md", id="numeric-input-low", placeholder='Minimum'),
                    html.P(id="number_type_low_text",
                           style={
                               'textAlign': 'right',
                               'color': colors['text']
                           })
                ],
            ), width={"size": 2}
            ),
            dbc.Col(html.Div(
                [
                    dbc.Input(type="number", size="md", id="numeric-input-high", placeholder='Maximum'),
                    html.P(id="number_type_high_text",
                            style={
                                'textAlign': 'right',
                                'color': colors['text']
                            })
                ],
            ), width={"size": 2}
            ),
            dbc.Col(
                html.Div([dcc.Dropdown(['Ascending', 'Descending'],
                                       id='order_by_order', placeholder='Order By', value='')
                          ],
                         ), width={"size": 2}),
        ],
        className="g-2"
    ),

    #Optional Filters
    # Filters
    dbc.Row(html.Div(html.H4("Standalone Filters"))),
    dbc.Row(
        [
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_dropdown_for_price_drops()[0],
                                           id='stock_dropdown', placeholder='Stock Symbol', value='')
                              ],
                             ), width={"size": 2}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_dropdown_for_price_drops()[1],
                                           id='company_dropdown', placeholder='Company Name', value='')
                              ],
                             ), width={"size": 4}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.sector_list(),
                                           id='sector_dropdown', placeholder='Sector', value='')
                              ],
                             ), width={"size": 3}),
            dbc.Col(html.Div([dcc.DatePickerRange(id='date_range',
                                                  start_date=date(2018, 6, 1),
                                                  end_date=get_dates(),
                                                  clearable=False)], ),
                    width={"size": 3}), ]),

    #checklist filters
    dbc.Row(dbc.Col(
        html.Div([
            html.H4("Select Data Type(s) to Generate a Table:"),
            dcc.Checklist(id='selected_columns',
                          options=[
                              {'label': 'Stock Data',
                               'value': ['Company Name', 'Stock Symbol', 'Price Change', 'Highest Price', 'Current Price',
                                         'Days Since Peak Price', 'Peak Price Date']},
                              {'label': 'Financial Data',
                               'value': ['Cash Growth Since Peak', 'Asset Growth Since Peak', 'Company Value Change',
                                         'Peak Company Value', 'Most Recent Company Value']},
                              {'label': 'EPS Data', 'value': ['EPS Change', 'EPS at Peak Price', 'Most Recent EPS']},
                              {'label': 'P/S Data',
                               'value': ['Price to Sales Ratio Change', 'Peak Price to Sales Ratio',
                                         'Most Recent Price to Sales Ratio']},
                              {'label': 'P/E Data',
                               'value': ['P/E Ratio Change', 'Peak P/E Ratio', 'Most Recent P/E Ratio']},
                              {'label': 'EBITDA Data',
                               'value': ['EBITDA Change', 'Peak Price EBITDA', 'Most Recent EBITDA']},
                          ],
                          value=[],
                          style={'padding': '5px'},
                          labelStyle={'font-size': '24px', 'font-family': 'Calibri'},
                          inputStyle={'margin-right': '4px', 'margin-left': '20px'},
                          ),
        ]), style={'padding-top': '20px'}
    )),

    #Button
    dbc.Row(html.P(id="big_data_error",
                   style={
                       'textAlign': 'left',
                       'color': colors['red_button']
                   })),
    dbc.Row(dbc.Col(
                html.Div([
                    dcc.Loading(id='loading_price_drop', fullscreen=False, color=colors['mid_theme'],
                                children=dbc.Button("Apply Filters",
                                                    id='price_drop_button',
                                                    className='d-grid gap-2',
                                                    n_clicks=0,
                                                    style={"background-color": colors['dark_theme'], "width": "100%"})),
                    html.Div(id='price_drop_output')
                ]), width={"size": 10, "offset": 1}
            )),

    #Price Drops Tables
    dbc.Row(html.P()),
    dbc.Row(dbc.Col(html.Div(id="price_drop_table"), width={"size": 12},)),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
    dbc.Row(html.P()),

    ##

    ##

    #revenue chart with filter
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),
    html.Div(html.H3(
        children='Quarterly Earnings by Stock Symbol',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),
    dbc.Row([
        dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_dropdown_for_price_drops()[0],
                                       id='stock_dropdown_rev_chart', placeholder='Stock Symbol', value='')
                          ],
                         ), width={"size": 2}),
        dbc.Col(
        html.Div([
            dcc.Loading(id='loading_revenue_chart', fullscreen=False, color=colors['mid_theme'],
                        children=dbc.Button("Apply Filters",
                                            id='revenue_chart_button',
                                            className='d-grid gap-2',
                                            n_clicks=0,
                                            style={"background-color": colors['dark_theme'], "width": "100%"})),
            html.Div(id='revenue_chart_output')
        ]), width={"size": 3}
    )]),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='revenue_chart', figure={})), width={"size": 9, "offset": 2})),
    ]
)

@callback(
    Output('number_type_low_text', 'children'),
    Output('number_type_high_text', 'children'),
    Input('order_by', 'value'),
)
def number_type_text(order_by):
    print(order_by)
    if order_by in ['Price Change', 'Cash Growth Since Peak', 'Asset Growth Since Peak', 'Company Value Change',
                    'EPS Change', 'Price to Sales Ratio Change', 'P/E Ratio Change', 'EBITDA Change']:
        number_type_text = '% (e.g. .1 = 10%)'
    elif order_by in ['Highest Price', 'Current Price', 'Peak Company Value', 'Most Recent Company Value',
                        'EPS at Peak Price', 'Most Recent EPS', 'Peak Price EBITDA', 'Most Recent EBITDA']:
        number_type_text = 'Dollar ($)'
    elif order_by in ['Days Since Peak Price', 'Peak Price to Sales Ratio', 'Most Recent Price to Sales Ratio',
                      'Peak P/E Ratio', 'Most Recent P/E Ratio']:
        number_type_text = 'Number'
    else:
        number_type_text = 'Not Applicable'
    number_type_low = number_type_text
    number_type_high = number_type_text
    return number_type_low, number_type_high

@callback(
    Output('big_data_error', 'children'),
    Input('price_drop_button', 'n_clicks'),
    [State('stock_dropdown', 'value'),
     State('company_dropdown', 'value'),
     State('sector_dropdown', 'value'),
     State("numeric-input-low", "value"),
     State("numeric-input-high", "value"),
     ],
    prevent_initial_call=True
)
def big_data_error(n_clicks, stock_dropdown, company_dropdown, sector_dropdown, numeric_input_low, numeric_input_high):
    big_data_error = ''
    if n_clicks > -1:
        print("1", stock_dropdown, "2", company_dropdown, "3", sector_dropdown, "4", numeric_input_low, "5", numeric_input_high)
        if stock_dropdown == '' and company_dropdown == '' and sector_dropdown == '' and numeric_input_low is None and numeric_input_high is None:
            big_data_error = "You requested a large dataset. Try applying some filters to improve the load time"
        else:
            big_data_error = ''
    print(n_clicks, "filter_applied")
    return big_data_error


##Table callback
@callback(
    Output('price_drop_table', 'children'),
    Output('price_drop_button', 'loading_state'),
    Output('filter_error_message', 'children'),
    Input('price_drop_button', 'n_clicks'),
    [State('stock_dropdown', 'value'),
    State('company_dropdown', 'value'),
     State('sector_dropdown', 'value'),
     State('date_range', 'start_date'),
     State('date_range', 'end_date'),
     State('order_by', 'value'),
     State('order_by_order', 'value'),
     State("selected_columns", "value"),
     State("numeric-input-low", "value"),
     State("numeric-input-high", "value"),
     ],
    prevent_initial_call=True
)
def price_drop_update_output(n_clicks, stock_dropdown, company_dropdown, sector_dropdown, start_date, end_date, order_by,
                             order_by_order, selected_columns, numeric_input_low, numeric_input_high):
    if len(start_date) > 0:
        #filtering for number inputs
        if numeric_input_low is None:
            numeric_input_low = float('-inf')
        else:
            numeric_input_low = numeric_input_low
        if numeric_input_high is None:
            numeric_input_high = float('inf')
        else:
            numeric_input_high = numeric_input_high
        print(type(numeric_input_low), numeric_input_low, numeric_input_high)
        if numeric_input_low >= numeric_input_high:
            numeric_input_low = float('-inf')
            numeric_input_high = float('inf')
            filter_error_message = 'Minimum value must be less than Maximum value'
        else:
            numeric_input_low = numeric_input_low
            numeric_input_high = numeric_input_high
            filter_error_message = ''

        selected_data = [value for sublist in selected_columns for value in sublist]
        print(n_clicks)
        price_drop_df = dataframes_from_queries.biggest_price_drop(stock_dropdown, company_dropdown, sector_dropdown,
                                                                   start_date, end_date, order_by, order_by_order,
                                                                   numeric_input_low, numeric_input_high)
        price_drop_df = price_drop_df[selected_data]
        #Steps to prevent slow loads
        if sector_dropdown == '':
            price_drop_df = price_drop_df.head(100)
        price_drop_table = my_dash_charts.generate_table_price_drops(price_drop_df)
        print("filter_applied")
    elif len(start_date) == 0:
        raise exceptions.PreventUpdate
    return price_drop_table, {'is_loading': True}, filter_error_message


#callback for the loading of the button
@callback(
    Output('price_drop_output', 'children'),
    Input('price_drop_button', 'n_clicks')
)
def update_output(n_clicks):
    if n_clicks is not None:
        time.sleep(5)


##
##


##Revenue Chart Callbacks
@callback(
    Output('revenue_chart', 'figure'),
    Output('revenue_chart_button', 'loading_state'),
    Input('revenue_chart_button', 'n_clicks'),
    [State('stock_dropdown_rev_chart', 'value'),
     ],
    prevent_initial_call=True
)
def revenue_chart_output(stock_filter):
    if len(stock_filter) > 0:
        revenue_chart_df = dataframes_from_queries.revenue_data_from_json_column(stock_filter)
        revenue_chart = my_dash_charts.annual_revenue_lines(revenue_chart_df, stock_filter)
        print("filter_applied")
    elif len(stock_filter) == 0:
        raise exceptions.PreventUpdate
    return revenue_chart, {'is_loading': True}


#callback for the loading of the button
@callback(
    Output('revenue_chart_output', 'children'),
    Input('revenue_chart_button', 'n_clicks')
)
def update_revenue_chart_output(n_clicks):
    if n_clicks is not None:
        time.sleep(5)
