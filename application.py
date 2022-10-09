import dash
from flask import Flask
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine
import passwords
import assets.images as my_images
import base64
import assets.sidebar as sidebar

url = passwords.rds_access
engine = create_engine(url)
connect = engine.connect()


app = Dash(__name__, use_pages=True, title='Causalation', serve_locally=False, external_stylesheets=[dbc.themes.LITERA])
server = Flask(__name__)
application = app.server


logo_image = my_images.logo
small_logo_image = my_images.small_logo
encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.Div(html.Img(src='data:image/png;base64,{}'.format(encoded_logo.decode()),
                                      style={'height': '5%', 'width': '70%'})),
                    width={"size": 6, "offset": 4})),
    dbc.Row(dbc.Col(html.Div(html.H4(children='Is it Correlation? Causation? Who knows, I just want to some alpha',
                                     style={'textAlign': 'center'})),
                    width={"size": 8, "offset": 2})),
    dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
    dbc.Row(dbc.Col(dash.page_container)),
]
)


#
# @server.route("/")
# def my_dash_app():
#     return app.index()



# if __name__ == '__main__':
#     application.run(debug=False)

if __name__ == '__main__':
    app.run_server(debug=True)