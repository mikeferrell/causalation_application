import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import time
from ml_models import dataframes_from_queries
import dash_components.charts as my_dash_charts
from cron_jobs import get_dates
from static.color_palette import colors
import static.stock_list as stock_lists
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


    #Filters
    dbc.Row(html.Div(html.H4(""))),
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
                    width={"size": 3}),]),
    dbc.Row([
            dbc.Col(html.Div([dcc.Dropdown(['Company Name', 'Stock Symbol', 'Price Change', 'Highest Price', 'Current Price',
                        'Days Since Peak Price', 'Peak Price Date', 'Cash Growth Since Peak', 'Asset Growth Since Peak',
                        'Company Value Change', 'Peak Company Value', 'Most Recent Company Value', 'EPS Change',
                        'EPS at Peak Price', 'Most Recent EPS',
                        'Price to Sales Ratio Change', 'Peak Price to Sales Ratio', 'Most Recent Price to Sales Ratio',
                        'P/E Ratio Change', 'Peak P/E Ratio', 'Most Recent P/E Ratio',
                        'EBITDA Change', 'Peak Price EBITDA', 'Most Recent EBITDA'],
                                           id='order_by', placeholder='Price Change', value='')
                              ],
                             ), width={"size": 3}),
            dbc.Col(html.Div(
                [
                    dbc.Input(type="number", size="md", step=1, id="numeric-input-low"),
                    html.P(id='number_type_low')
                ],
            ), width={"size": 2}
            ),
            dbc.Col(html.Div(
                [
                    dbc.Input(type="number", size="md", step=1, id="numeric-input-high"),
                    html.P(id='number_type_high')
                ],
            ), width={"size": 2}
            ),
        dbc.Col(html.Div(html.P(id="number_type_low_text"))),
            dbc.Col(
                html.Div([dcc.Dropdown(['Ascending', 'Descending'],
                                       id='order_by_order', placeholder='Order By', value='Ascending')
                          ],
                         ), width={"size": 2}),
        ],
        className="g-2"
    ),

    #checklist filters
    dbc.Row(dbc.Col(
        html.Div([
            html.H4("Select Data Type(s) to Generate a Table:"),
            dcc.Checklist(id='selected_columns',
                          options=[
                              {'label': 'Stock Data',
                               'value': ['Stock Symbol', 'Price Change', 'Highest Price', 'Current Price',
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
        ]),
    )),

    #Button
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
    ]
)


@callback(
    Output('price_drop_table', 'children'),
    Output('price_drop_button', 'loading_state'),
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
)
def price_drop_update_output(n_clicks, stock_dropdown, company_dropdown, sector_dropdown, start_date, end_date, order_by,
                             order_by_order, selected_columns, numeric_input_low, numeric_input_high):
    if len(start_date) > 0:
        #filtering for number inputs
        if numeric_input_low is None:
            numeric_input_low = -100000000000
        else:
            numeric_input_low = numeric_input_low
        if numeric_input_high is None:
            numeric_input_high = 100000000000
        else:
            numeric_input_high = numeric_input_high
        print(type(numeric_input_low), numeric_input_low, numeric_input_high)
        if numeric_input_low >= numeric_input_high:
            numeric_input_low = -100000000000
            numeric_input_high = 100000000000
        else:
            numeric_input_low = numeric_input_low
            numeric_input_high = numeric_input_high

        selected_data = [value for sublist in selected_columns for value in sublist]
        print(n_clicks)
        price_drop_df = dataframes_from_queries.biggest_price_drop(stock_dropdown, company_dropdown, sector_dropdown,
                                                                   start_date, end_date, order_by, order_by_order)
        price_drop_df = price_drop_df.head(100)
        price_drop_df = price_drop_df[selected_data]
        price_drop_table = my_dash_charts.generate_table_price_drops(price_drop_df)
        print("filter_applied")
        # numeric_input_low = float(numeric_input_low)
        # numeric_input_high = float(numeric_input_high)
        numbers = numeric_input_low, numeric_input_high
        print(numbers)
    elif len(start_date) == 0:
        raise exceptions.PreventUpdate
    return price_drop_table, {'is_loading': True}

@callback(
    Output('number_type_low_text', 'children'),
    Output('number_type_high_text', 'children'),
    Input('order_by', 'value'),
)
def number_type_text(order_by):
    if order_by in ['Price Change', 'Cash Growth Since Peak', 'Asset Growth Since Peak', 'Company Value Change',
                    'EPS Change', 'Price to Sales Ratio Change', 'P/E Ratio Change', 'EBITDA Change',]:
        number_type_text = '%'
    elif order_by in ['Highest Price', 'Current Price', 'Peak Company Value', 'Most Recent Company Value',
                        'EPS at Peak Price', 'Most Recent EPS', 'Peak Price EBITDA', 'Most Recent EBITDA']:
        number_type_text = '$'
    elif order_by in ['Days Since Peak Price', 'Peak Price to Sales Ratio', 'Most Recent Price to Sales Ratio',
                      'Peak P/E Ratio', 'Most Recent P/E Ratio']:
        number_type_text = 'Number'
    else:
        number_type_text = 'N/A'
    number_type_low = number_type_text
    number_type_high = number_type_text
    return number_type_low, number_type_high


#callback for the loading of the button
@callback(
    Output('price_drop_output', 'children'),
    Input('price_drop_button', 'n_clicks')
)
def update_output(n_clicks):
    if n_clicks is not None:
        time.sleep(5)
