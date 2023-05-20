import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from static.color_palette import colors
import static.images as images

dash.register_page(__name__, path='/blog')


layout = dbc.Container([
    # image
    dbc.Row([dbc.Col(html.Div(html.Img(src=images.logo_image_direct,
                                       style={'height': '2%', 'width': '50%'})),
                     width={"size": 6, "offset": 4}),
             ]),
    dbc.Row(html.Div(html.Hr(className="my-2"))),
    dbc.Row(html.Div(html.H1(""))),

    dbc.Row(
        dbc.Col(html.Div([
            html.H1('''Blog''')
        ]),
            style={'textAlign': 'center', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(
        dbc.Col(html.Div([
            html.H4('''Follow along as I improve the model 
            and attempt to beat the market by blindly trusting it's recommendations''')
        ]),
            style={'textAlign': 'center', 'fontWeight': '300', 'color': colors['text']},
            width={"size": 8, "offset": 2}
        )
    ),
    dbc.Row(html.Div([html.Hr(className="my-2"),
                      html.H1("")],
                     style={'padding': 15}),
            className="h-10"),

    #blog pages
    dbc.Row(
        dbc.Col(html.Div([
            dbc.NavLink(html.H3("Update 5/14/2023"),
                        href="/blog_pages/5_14_23_blog"),
            dbc.NavLink(html.H3("Update 5/7/2023"),
                        href="/blog_pages/5_7_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 3/12/2023"),
                                      href="/blog_pages/3_12_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 3/5/2023"),
                                      href="/blog_pages/3_5_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(
        dbc.Col(html.Div([dbc.NavLink(html.H3("Update 2/18/2023"),
                                      href="/blog_pages/2_18_23_blog"),
                          ]),
                style={'textAlign': 'center', 'color': colors['mid_theme']},
                width={"size": 8, "offset": 2},
                )
    ),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
    dbc.Row(html.P()),
])

