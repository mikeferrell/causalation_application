import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from dash.dash_table import DataTable
from static.color_palette import colors
import passwords

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()



def Mult_Y_Axis_Lines(dataframe_input, stock_name):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"close_date"], y=dataframe_input.loc[:,"close_price"], name=stock_name),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"close_date"], y=dataframe_input.loc[:,"coin_price"], name="Crypto"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Top Stock and Crypto Correlated with a 1 month Delay"
    )
    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=False)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    return fig


def Edgar_Mult_Y_Axis_Lines(dataframe_input, stock_name, keyword):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"week_opening_date"], y=dataframe_input.loc[:,"week_close_price"], name=stock_name),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"week_opening_date"],
                   y=dataframe_input.loc[:,f"{keyword} Mentions Rolling Average"], name=f"{keyword} Mention Percentage"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Stock Most Correlated with Keyword Mentions in Public Filings"
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    # Set y-axes titles
    fig.update_yaxes(title_text=f"<b>{stock_name}</b> Closing Price", secondary_y=False)
    fig.update_yaxes(title_text=f"<b>{keyword}</b> Count", secondary_y=True)

    return fig

def backtest_Mult_Y_Axis_Lines(dataframe_input):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"week_of_purchases"], y=dataframe_input.loc[:,"portfolio_value"],
                   name="Value of my Portfolio"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=dataframe_input.loc[:,"week_of_purchases"],
                   y=dataframe_input.loc[:,"s_and_p_price"], name="S&P 500 Price"),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text="Backtested Performance vs S&P 500"
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Date")
    # Set y-axes titles
    fig.update_yaxes(title_text=f"<b>Backtested Value", range=[1000, 2000], secondary_y=False)
    fig.update_yaxes(title_text=f"<b>S&P 500 Value", range=[3500, 7000], secondary_y=True)

    return fig


def generate_table(dataframe):
    table = dbc.Table.from_dataframe(dataframe, striped=True, bordered=True, hover=True, responsive=True)
    return table

def generate_table_price_drops(dataframe):
    table = DataTable(
        id='datatable',
        data=dataframe.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in dataframe.columns],
        fixed_rows={'headers': True},
        style_table={'overflowY': 'scroll'},
        style_data={
            'font-family': 'Calibri'
        },
        style_cell={'padding': '5px',
                    'textAlign': 'center',
                    'minWidth': '100px',
                    },
        style_header={
            'position': 'sticky',
            'top': '0',
            'backgroundColor': colors['mid_theme'],
            'color': 'white',
            'whiteSpace': 'normal',
            'overflow': 'auto'
        },
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': colors['light_theme']
        }],
    )

    return table



def generate_table_with_filters(dataframe):
    table = DataTable(data=dataframe.to_dict('records'), columns=[{"name": i, "id": i} for i in dataframe.columns],
                      filter_action='native',
                      style_data={
                        'width': '150px', 'minWidth': '50px', 'maxWidth': '100px',
                        'overflow': 'hidden',
                        'textOverflow': 'inherit',
                        'font-family': 'Calibri'
                      },
                      style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': colors['light_theme']}
                                              ],
                      style_as_list_view=True,
                      style_cell={'padding': '5px', 'textAlign': 'center'},
                      style_header={
                          'backgroundColor': colors['mid_theme'],
                          'fontWeight': '400',
                          'color': 'white',
                      },
                      )

    return table





