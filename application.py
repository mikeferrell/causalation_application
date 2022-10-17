import dash
from flask import Flask
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import images as my_images
import base64
import sidebar as sidebar


app = Dash(__name__, use_pages=True, title='Causalation', assets_folder="static", assets_url_path="static",
           external_stylesheets=[dbc.themes.LITERA])
server = Flask(__name__)
application = app.server

logo_image_direct = 'static/causalation-logo-no-background.png'
# logo_image = my_images.logo
# small_logo_image = my_images.small_logo
# encoded_logo = base64.b64encode(open(logo_image, 'rb').read())
# encoded_small_logo = base64.b64encode(open(small_logo_image, 'rb').read())

colors = {
    'background': '#FFFFFF',
    'text': '#000000'
}

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.Div(html.Img(src=logo_image_direct,
                                      style={'height': '5%', 'width': '70%'})),
                    width={"size": 6, "offset": 4})),
    dbc.Row(dbc.Col(html.Div([dcc.Location(id="url"), sidebar.sidebar, sidebar.content]), width=6)),
    dbc.Row(dbc.Col(dash.page_container)),
]
)


@server.route("/")
def my_dash_app():
    return app.index()


if __name__ == '__main__':
    application.run(port=8000, debug=False)
#
# if __name__ == '__main__':
#     app.run_server(port=8000, debug=False)