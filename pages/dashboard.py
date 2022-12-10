import dash
from dash import dcc, html, Input, Output, State, exceptions, callback
import dash_bootstrap_components as dbc
from datetime import date
import dataframes_from_queries
import dash_components.charts as my_dash_charts
import sidebar as sidebar
from cron_jobs import get_dates

dash.register_page(__name__, path='/dashboard', name="Dashboard")

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}


layout = html.Div(children=
                  [dbc.Container([
    dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
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
            dbc.Col(html.Div([dcc.Dropdown(['10-K', '10-Q'],
                                           id='filing_type_dropdown_input', value='10-K')
                              ],
                             ), width={"size": 1}),
            dbc.Col(html.Div([dcc.Dropdown(dataframes_from_queries.keyword_list,
                                           id='keyword_dropdown_input', value='cloud')
                              ],
                             ), width={"size": 2}),
            dbc.Col(html.Div(dbc.Button("Apply Filters", id='my_button', color="primary", className="me-1", n_clicks=0)
                             ),
                    width={"size": 2})
        ],
        className="g-2"
    ),
    dbc.Row(dbc.Col(html.Div(dcc.Graph(id='date_and_stock_for_chart', figure={})), width={"size": 9, "offset": 2})),
    dbc.Row([
        # dbc.Col(html.Div(id="correlation_table"), width={"size": 3, "offset": 2}),
        dbc.Col(html.Div(id="keyword_count_table"), width={"size": 3, "offset": 2}),
        dbc.Col(html.Div(id="keyword_correlation_table"), width={"size": 3, "offset": 1})
    ]),
    html.Div(html.H1(
        children='Top Stock Correlations',
        style={
            'textAlign': 'center',
            'color': colors['text']
        })),
    dbc.Row(
        [
            dbc.Col(html.Div(id="desc_correlation_table"), width={"size": 3, "offset": 2}),
            dbc.Col(html.Div(id="asc_correlation_table"), width={"size": 3, "offset": 1})
        ]
    ),
      html.Div(html.H1(
          children='Data from Chart Above',
          style={
              'textAlign': 'center',
              'color': colors['text']
          })),
      dbc.Row(
              dbc.Col(html.Div(id="data_from_chart"), width={"size": 6, "offset": 3})
      )
        ])
                  ])

@callback(
    Output('date_and_stock_for_chart', 'figure'),
    # Output('correlation_table', 'children'),
    Output('keyword_correlation_table', 'children'),
    Output('keyword_count_table', 'children'),
    Output('desc_correlation_table', 'children'),
    Output('asc_correlation_table', 'children'),
    Output('data_from_chart', 'children'),
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
        edgar_chart = my_dash_charts.Edgar_Mult_Y_Axis_Lines(
            dataframes_from_queries.inflation_mention_chart(stock_dropdown_value, start_date,
                                                            end_date, keyword_dropdown_value, ''),
            stock_dropdown_value, keyword_dropdown_value)
        # dropdown_table = my_dash_charts.generate_table(
        #     dataframes_from_queries.stock_crypto_correlation_filtered(stock_dropdown_value))
        keyword_correlation_table = my_dash_charts.generate_table(
            dataframes_from_queries.inflation_mention_correlation(stock_dropdown_value, start_date,
                                                                  end_date, keyword_dropdown_value,
                                                                  week_delay_dropdown_value))
        keyword_count_table = my_dash_charts.generate_table(
            dataframes_from_queries.keyword_table(keyword_dropdown_value, start_date, end_date))
        descending_correlation_table = my_dash_charts.generate_table(
                dataframes_from_queries.top_keyword_correlations_with_rolling_avg('desc', keyword_dropdown_value,
                                                                    start_date, end_date, week_delay_dropdown_value)),
        ascending_correlation_table = my_dash_charts.generate_table(
                dataframes_from_queries.top_keyword_correlations_with_rolling_avg('asc', keyword_dropdown_value,
                                                                    start_date, end_date, week_delay_dropdown_value)),
        data_from_chart = my_dash_charts.generate_table(
            dataframes_from_queries.inflation_mention_chart(stock_dropdown_value, start_date,
                                                            end_date, keyword_dropdown_value, 'limit 30'))
        print("filter_applied")
    elif len(stock_dropdown_value) == 0:
        raise exceptions.PreventUpdate
    return edgar_chart, keyword_correlation_table, \
           keyword_count_table, descending_correlation_table, ascending_correlation_table, data_from_chart