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
    html.Div(html.H4(
        children='Compare current company financials with their financial status at peak stock price',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),


    #Filters
    dbc.Row(html.Div(html.H4(""))),
    dbc.Row(
        [
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.stock_dropdown_for_price_drops(),
                                           id='stock_dropdown', placeholder='Stock', value='')
                              ],
                             ), width={"size": 1    }),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.sector_list(),
                                           id='sector_dropdown', placeholder='Sector', value='')
                              ],
                             ), width={"size": 3}),
            dbc.Col(html.Div([dcc.DatePickerRange(id='date_range',
                                                  start_date=date(2018, 6, 1),
                                                  end_date=get_dates(),
                                                  clearable=False)], ),
                    width={"size": 3}),
            dbc.Col(html.Div([dcc.Dropdown(['Stock Symbol', 'Peak Price EBITDA', 'Price Change', 'Asset Growth Since Peak',
                                            'Cash Growth Since Peak',
                                            'Peak Company Value', 'Most Recent Company Value', 'Company Value Change',
                                            'EPS Change', 'Price to Sales Ratio Change', 'P/E Ratio Change',
                                            'EBITDA Change'],
                                           id='order_by', placeholder='Order By', value='')
                              ],
                             ), width={"size": 3}),
            dbc.Col(
                html.Div([dcc.Dropdown(['Ascending', 'Descending'],
                                       id='order_by_order', placeholder='Ascending', value='Ascending')
                          ],
                         ), width={"size": 2}),
        ],
        className="g-2"
    ),

    #checklist filters
    dbc.Row(dbc.Col(
        html.Div([
            html.H4("Select Data Type(s) to Generate a Table"),
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
                                children=dbc.Button("Apply Filters", id='price_drop_button', className='d-grid gap-2',
                                                    n_clicks=0, style={"background-color": colors['mid_theme']})),
                    html.Div(id='price_drop_output')
                ]), width={"size": 10, "offset": 1}
            )),

    #Price Drops Tables
    dbc.Row(dbc.Col(html.Div(id="price_drop_table"), width={"size": 12},))
    ])


@callback(
    Output('price_drop_table', 'children'),
    Output('price_drop_button', 'loading_state'),
    # Output('column-selection', 'options'),
    # Output('eps_table', 'children'),
    Input('price_drop_button', 'n_clicks'),
    [State('stock_dropdown', 'value'),
     State('sector_dropdown', 'value'),
     State('date_range', 'start_date'),
     State('date_range', 'end_date'),
     State('order_by', 'value'),
     State('order_by_order', 'value'),
     State("selected_columns", "value"),
     ],
)
def price_drop_update_output(n_clicks, stock_dropdown, sector_dropdown, start_date, end_date, order_by, order_by_order,
                             selected_columns):
    if len(start_date) > 0:
        selected_data = [value for sublist in selected_columns for value in sublist]

        # if selected_columns is None:
        #     selected_columns = 'Stock Symbol'
        # else:
        #     selected_columns = selected_columns.split(',')
        print(n_clicks)
        price_drop_df = dataframes_from_queries.biggest_price_drop(stock_dropdown, sector_dropdown, start_date, end_date,
                                                                   order_by, order_by_order)
        price_drop_df = price_drop_df.head(100)
        price_drop_df = price_drop_df[selected_data]
        price_drop_table = my_dash_charts.generate_table_price_drops(price_drop_df)
        print("filter_applied")
    elif len(start_date) == 0:
        raise exceptions.PreventUpdate
    return price_drop_table, {'is_loading': True}


#callback for the loading of the button
@callback(
    Output('price_drop_output', 'children'),
    Input('price_drop_button', 'n_clicks')
)
def update_output(n_clicks):
    if n_clicks is not None:
        time.sleep(5)


# @callback(
# Output('collapse_eps_table', 'is_open'),
# [Input('collapse-button-price-drop', 'n_clicks')],
# State('collapse_eps_table', 'is_open')
# )
# def toggle_collapse_table(n_clicks, is_open):
#     if n_clicks:
#         return not is_open
#     return is_open