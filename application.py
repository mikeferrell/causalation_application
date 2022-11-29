import dash
from flask import Flask
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import images as my_images
import base64
import sidebar as sidebar
import cron_jobs
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os


app = Dash(__name__, use_pages=True, title='Causalation', assets_folder="static", assets_url_path="static",
           external_stylesheets=[dbc.themes.LITERA])
server = Flask(__name__)
scheduler = BackgroundScheduler()
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


# scheduler.add_job(cron_jobs.full_edgar_job_10ks, 'cron', hour=15, minute=21, name='full_edgar_10ks')
scheduler.add_job(cron_jobs.update_stock_data, 'cron', day_of_week='tue-sat', hour=4, minute=20)
# scheduler.add_job(cron_jobs.keyword_count_cron_job, 'cron', day_of_week='tue-sat', hour=4, minute=10)
# scheduler.add_job(cron_jobs.weekly_stock_opening_cron_job, 'cron', day_of_week='tue-sat', hour=4, minute=15)
scheduler.start()


if __name__ == '__main__':
    application.run(port=8000, debug=False)
#
# if __name__ == '__main__':
#     app.run_server(port=8000, debug=False)