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
        children='Price Drops from All Time Highs',
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
            dbc.Col(html.Div([dcc.Dropdown(stock_lists.stock_list,
                                           id='stock_dropdown', placeholder='Stock', value='')
                              ],
                             ), width={"size": 1, "offset": 1}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.sector_list(),
                                           id='sector_dropdown', placeholder='Sector', value='')
                              ],
                             ), width={"size": 3}),
            dbc.Col(html.Div([dcc.DatePickerRange(id='date_range',
                                                  start_date=date(2017, 1, 1),
                                                  end_date=get_dates(),
                                                  clearable=False)], ),
                    width={"size": 3}),
            dbc.Col(html.Div([dcc.Dropdown(['stock_symbol', 'highest_price_date', 'highest_price', 'Sector',
                                            'asset_growth_since_peak', 'cash_growth_since_peak', 'price_drop',
                                            'days_since_ath'],
                                           id='order_by', placeholder='Order By', value='')
                              ],
                             ), width={"size": 2}),
            dbc.Col(
                html.Div([
                    dcc.Loading(id='loading_price_drop', fullscreen=False, color=colors['mid_theme'],
                                children=dbc.Button("Apply Filters", id='price_drop_button', className="me-1", n_clicks=0,
                                                    style={"background-color": colors['mid_theme']})),
                    html.Div(id='price_drop_output')
                ]),
            )
        ],
        className="g-2"
    ),


    #Price Drops Tables
    dbc.Row(dbc.Col(html.Div(id="price_drop_table"), width={"size": 10, "offset": 1})),

    ])


@callback(
    Output('price_drop_table', 'children'),
    Input('price_drop_button', 'n_clicks'),
    [State('stock_dropdown', 'value'),
     State('sector_dropdown', 'value'),
     State('date_range', 'start_date'),
     State('date_range', 'end_date'),
     State('order_by', 'value')
     ],
    prevent_initial_call=False,
)
def price_drop_update_output(n_clicks, stock_dropdown, sector_dropdown, start_date, end_date, order_by):
    if len(start_date) > 0:
        print(n_clicks)
        price_drop_table = my_dash_charts.generate_table(
            dataframes_from_queries.biggest_price_drop(stock_dropdown, sector_dropdown, start_date, end_date, order_by))
        print("filter_applied")
    elif len(start_date) == 0:
        raise exceptions.PreventUpdate
    return price_drop_table


#callback for the loading of the button
@callback(
    Output('price_drop_output', 'children'),
    Input('price_drop_button', 'n_clicks')
)
def update_output(n_clicks):
    if n_clicks is not None:
        time.sleep(5)
